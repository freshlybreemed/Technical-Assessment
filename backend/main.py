from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import requests
import os
import re
from helpers import *

app = Flask(__name__)

# Simple CORS configuration - allow all origins
CORS(app, origins="*", supports_credentials=False)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@app.route("/filters", methods=["GET", "OPTIONS"])
def get_filters():
    """
    Get available filters
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        filters = get_available_filters()
        return jsonify({"filters": filters}), 200
    except Exception as e:
        logger.error(f"Error getting filters: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "message": "Video Background Filter API is running"}), 200

@app.route("/cors-test", methods=["GET", "POST", "OPTIONS"])
def cors_test():
    """
    Test CORS functionality
    """
    if request.method == "OPTIONS":
        return "", 200
    
    return jsonify({
        "message": "CORS test successful",
        "method": request.method,
        "timestamp": "2024-01-01T00:00:00Z"
    }), 200

@app.route("/chunk-test", methods=["GET", "POST", "OPTIONS"])
def chunk_test():
    """
    Test chunk endpoints CORS functionality
    """
    if request.method == "OPTIONS":
        return "", 200
    
    return jsonify({
        "message": "Chunk CORS test successful",
        "method": request.method,
        "endpoints": ["/chunk/start", "/chunk/status", "/chunk/finish", "/chunk/list", "/chunk/download"]
    }), 200

@app.route("/process-video", methods=["POST", "OPTIONS"])
def process_video():
    """
    Start processing an entire video with background filtering
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        video_url = data.get('videoUrl')
        filter_type = data.get('filterType', 'grayscale')
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Start video processing in background
        job_id = start_video_processing(video_url, filter_type)
        
        return jsonify({
            "message": "Video processing started",
            "jobId": job_id,
            "filterType": filter_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting video processing: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/processing-status/<job_id>", methods=["GET", "OPTIONS"])
def get_processing_status_route(job_id):
    """
    Get status of video processing job
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        status = get_processing_status(job_id)
        if status:
            return jsonify(status), 200
        else:
            return jsonify({"error": "Job not found"}), 404
            
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/processed-videos", methods=["GET", "OPTIONS"])
def list_processed_videos():
    """
    List all processed videos
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        videos = get_processed_videos()
        return jsonify({"videos": videos}), 200
        
    except Exception as e:
        logger.error(f"Error listing processed videos: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/processed-video/download/<filename>", methods=["GET"])
def download_processed_video(filename):
    """
    Download a processed video
    """
    try:
        filepath = os.path.join("processed_videos", filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        logger.error(f"Error downloading processed video: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/processed-video/stream/<filename>", methods=["GET", "OPTIONS"])
def stream_processed_video(filename):
    """
    Stream a processed video for playback
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        filepath = os.path.join("processed_videos", filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # Simple streaming without range requests for now
        response = send_file(
            filepath, 
            mimetype='video/mp4',
            as_attachment=False,
            conditional=True
        )
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Range'
        response.headers['Accept-Ranges'] = 'bytes'
        
        return response
        
    except Exception as e:
        logger.error(f"Error streaming processed video: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/mask-preview", methods=["POST", "OPTIONS"])
def get_mask_preview():
    """
    Get a preview of person detection mask
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        video_url = data.get('videoUrl')
        frame_number = data.get('frameNumber', 0)
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Open video and get specific frame
        cap = cv2.VideoCapture(video_url)
        if not cap.isOpened():
            return jsonify({"error": "Could not open video"}), 400
        
        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({"error": "Could not read frame"}), 400
        
        # Create mask preview
        preview = create_mask_preview(frame)
        
        # Convert to base64
        _, buffer = cv2.imencode('.jpg', preview)
        preview_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "preview": f"data:image/jpeg;base64,{preview_base64}",
            "frameNumber": frame_number
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating mask preview: {e}")
        return jsonify({"error": str(e)}), 500



@app.route("/video-proxy", methods=["GET"])
def video_proxy():
    """
    Proxy endpoint to fetch and serve video files
    This avoids CORS issues by serving the video from the backend
    """
    try:
        # Get video URL from query parameter
        video_url = request.args.get('url')
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Fetch the video from the external source
        response = requests.get(video_url, stream=True)
        
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch video: {response.status_code}"}), 500
        
        # Create a streaming response
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                yield chunk
        
        # Return the video with proper headers
        return Response(
            generate(),
            content_type=response.headers.get('content-type', 'video/mp4'),
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Length': response.headers.get('content-length', ''),
                'Accept-Ranges': 'bytes'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in video proxy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/video-urls", methods=["GET"])
def get_video_urls():
    """
    Get available video URLs that can be proxied
    """
    try:
        video_urls = [
            {
                "id": "primary",
                "name": "Primary Video",
                "url": "https://storage.googleapis.com/rizeo-40249.appspot.com/01a23584-c6dc-4e70-b82e-8058f3db090e.mp4"
            },

        ]
        
        return jsonify({"videoUrls": video_urls}), 200
        
    except Exception as e:
        logger.error(f"Error getting video URLs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chunk/start", methods=["POST", "OPTIONS"])
def start_video_chunk():
    """
    Start a new video chunk recording
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        filter_type = data.get('filterType', 'grayscale')
        
        # Reset any existing chunk
        finish_video_chunk()
        
        return jsonify({
            "message": "Video chunk recording started",
            "filterType": filter_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting video chunk: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chunk/status", methods=["GET", "OPTIONS"])
def get_video_chunk_status():
    """
    Get status of current video chunk
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        status = get_chunk_status()
        if status:
            return jsonify(status), 200
        else:
            return jsonify({"message": "No active video chunk"}), 200
            
    except Exception as e:
        logger.error(f"Error getting chunk status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chunk/finish", methods=["POST", "OPTIONS"])
def finish_video_chunk_endpoint():
    """
    Finish current video chunk and return download link
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        filepath = finish_video_chunk()
        
        if filepath and os.path.exists(filepath):
            # Return file info for download
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
            
            return jsonify({
                "message": "Video chunk completed",
                "filename": filename,
                "filepath": filepath,
                "fileSize": file_size,
                "downloadUrl": f"/chunk/download/{filename}"
            }), 200
        else:
            return jsonify({"error": "No video chunk to finish"}), 400
            
    except Exception as e:
        logger.error(f"Error finishing video chunk: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chunk/download/<filename>", methods=["GET"])
def download_video_chunk(filename):
    """
    Download a completed video chunk
    """
    try:
        filepath = os.path.join("temp_videos", filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        logger.error(f"Error downloading video chunk: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/chunk/list", methods=["GET", "OPTIONS"])
def list_video_chunks():
    """
    List all available video chunks
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        chunks_dir = "temp_videos"
        if not os.path.exists(chunks_dir):
            return jsonify({"chunks": []}), 200
        
        chunks = []
        for filename in os.listdir(chunks_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(chunks_dir, filename)
                file_size = os.path.getsize(filepath)
                chunks.append({
                    "filename": filename,
                    "fileSize": file_size,
                    "downloadUrl": f"/chunk/download/{filename}"
                })
        
        return jsonify({"chunks": chunks}), 200
        
    except Exception as e:
        logger.error(f"Error listing video chunks: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/cache/info", methods=["GET", "OPTIONS"])
def get_cache_info_route():
    """
    Get cache statistics
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        cache_info = get_cache_info()
        return jsonify(cache_info), 200
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/cache/clear", methods=["POST", "OPTIONS"])
def clear_cache_route():
    """
    Clear all cached videos
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        success = clear_cache()
        if success:
            return jsonify({"message": "Cache cleared successfully"}), 200
        else:
            return jsonify({"error": "Failed to clear cache"}), 500
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/pre-generate/samples", methods=["POST", "OPTIONS"])
def pre_generate_samples_route():
    """
    Pre-generate sample videos with all filters
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        pre_generate_sample_videos()
        return jsonify({"message": "Sample videos added to pre-generation queue"}), 200
    except Exception as e:
        logger.error(f"Error pre-generating samples: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/pre-generate/status", methods=["GET", "OPTIONS"])
def get_pre_generation_status_route():
    """
    Get pre-generation queue status
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        status = get_pre_generation_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting pre-generation status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/pre-generate/add", methods=["POST", "OPTIONS"])
def add_to_pre_generation_route():
    """
    Add a video to pre-generation queue
    """
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        video_url = data.get('videoUrl')
        filter_type = data.get('filterType', 'grayscale')
        
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
        
        add_to_pre_generation_queue(video_url, filter_type)
        return jsonify({"message": "Video added to pre-generation queue"}), 200
        
    except Exception as e:
        logger.error(f"Error adding to pre-generation queue: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
