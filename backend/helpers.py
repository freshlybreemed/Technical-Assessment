import logging
import ffmpeg
import os
import uuid
import cv2
import numpy as np
from PIL import Image
import base64
import io
import tempfile
from datetime import datetime
import threading
import time
import hashlib
import json

# Load the pre-trained Haar cascade classifiers
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_temp_path():
    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    random_filename = f"temp_{str(uuid.uuid4())[:8]}"
    return os.path.join(temp_dir, random_filename)

def detect_person(frame):
    """
    Detect person in the frame using face and body detection
    Returns a mask where person is detected
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.05, 
        minNeighbors=3, 
        minSize=(20, 20)
    )
    
    # Detect full body
    bodies = body_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=2,
        minSize=(40, 80)
    )
    
    # Create mask for detected regions
    mask = np.zeros(gray.shape, dtype=np.uint8)
    
    # Add face regions to mask
    for (x, y, w, h) in faces:
        # Expand the face region to include more of the person
        expanded_x = max(0, x - w//2)
        expanded_y = max(0, y - h//2)
        expanded_w = min(frame.shape[1] - expanded_x, w * 2)
        expanded_h = min(frame.shape[0] - expanded_y, h * 3)
        
        cv2.rectangle(mask, (expanded_x, expanded_y), 
                      (expanded_x + expanded_w, expanded_y + expanded_h), 255, -1)
    
    # Add body regions to mask
    for (x, y, w, h) in bodies:
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    
    # Apply morphological operations to smooth the mask
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Apply Gaussian blur to create smooth edges
    mask = cv2.GaussianBlur(mask, (21, 21), 0)
    
    return mask

def apply_background_filter(frame, filter_type):
    """
    Apply filter to background while keeping person in original colors
    """
    # Detect person in the frame
    person_mask = detect_person(frame)
    
    # Normalize mask to 0-1 range
    person_mask = person_mask.astype(np.float32) / 255.0
    
    # Apply filter using the mask
    return apply_background_filter_with_mask(frame, filter_type, person_mask)

def create_mask_preview(frame):
    """
    Create a preview showing the detected person mask
    """
    # Detect person in the frame
    mask = detect_person(frame)
    
    # Create a colored mask overlay
    mask_colored = np.zeros_like(frame)
    mask_colored[mask > 127] = [0, 255, 0]  # Green for detected person
    
    # Blend with original frame
    alpha = 0.3
    preview = cv2.addWeighted(frame, 1-alpha, mask_colored, alpha, 0)
    
    # Add text
    cv2.putText(preview, "Person Detection Preview", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return preview



def apply_background_filter_with_mask(frame, filter_type, person_mask):
    """
    Apply filter to background using pre-computed mask for faster processing
    """
    # Apply filter to the entire frame
    if filter_type == 'grayscale':
        # Use weighted grayscale conversion for better quality
        filtered_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply slight contrast enhancement
        filtered_frame = cv2.convertScaleAbs(filtered_frame, alpha=1.1, beta=5)
        filtered_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'sepia':
        filtered_frame = apply_sepia_filter(frame)
    elif filter_type == 'blur':
        filtered_frame = cv2.GaussianBlur(frame, (21, 21), 0)
    else:
        filtered_frame = frame.copy()
    
    # Apply additional smoothing to the mask for better blending
    smoothed_mask = cv2.GaussianBlur(person_mask, (15, 15), 0)
    smoothed_mask_3d = np.stack([smoothed_mask] * 3, axis=2)
    
    # Blend with smoothed mask for better transitions
    result = frame * smoothed_mask_3d + filtered_frame * (1 - smoothed_mask_3d)
    
    return result.astype(np.uint8)

def apply_sepia_filter(frame):
    """
    Apply sepia filter to the frame
    """
    # Sepia transformation matrix
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    
    # Apply transformation
    sepia_frame = cv2.transform(frame, sepia_matrix)
    
    # Clip values to valid range
    sepia_frame = np.clip(sepia_frame, 0, 255).astype(np.uint8)
    
    return sepia_frame



def get_available_filters():
    """
    Get list of available filters
    """
    return [
        {"id": "grayscale", "name": "Grayscale", "description": "Convert background to grayscale"},
        {"id": "sepia", "name": "Sepia", "description": "Apply sepia tone to background"},
        {"id": "blur", "name": "Blur", "description": "Blur the background"}
    ]

class VideoProcessor:
    """
    Class to handle complete video processing with caching
    """
    def __init__(self, output_dir="processed_videos"):
        self.output_dir = output_dir
        self.processing_jobs = {}  # Store processing status for each job
        self.cache_index = {}  # Store cache mapping: (video_url, filter_type) -> filename
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load existing cache from disk
        self.load_cache()
    
    def load_cache(self):
        """
        Load cache index from disk
        """
        cache_file = os.path.join(self.output_dir, "cache_index.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
                self.cache_index = {}
    
    def save_cache(self):
        """
        Save cache index to disk
        """
        cache_file = os.path.join(self.output_dir, "cache_index.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def get_cache_key(self, video_url, filter_type):
        """
        Generate a cache key for video URL and filter type
        """
        # Create a hash of the video URL to use as part of the cache key
        import hashlib
        url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
        return f"{url_hash}_{filter_type}"
    
    def is_cached(self, video_url, filter_type):
        """
        Check if a video with given URL and filter is already cached
        """
        cache_key = self.get_cache_key(video_url, filter_type)
        if cache_key in self.cache_index:
            filename = self.cache_index[cache_key]
            filepath = os.path.join(self.output_dir, filename)
            # Check if the cached file still exists
            if os.path.exists(filepath):
                return filename
        return None
    
    def add_to_cache(self, video_url, filter_type, filename):
        """
        Add a processed video to cache
        """
        cache_key = self.get_cache_key(video_url, filter_type)
        self.cache_index[cache_key] = filename
        self.save_cache()
    
    def process_video(self, video_url, filter_type, job_id):
        """
        Process entire video and save as filtered video
        """
        try:
            # Check if video is already cached
            cached_filename = self.is_cached(video_url, filter_type)
            if cached_filename:
                # Video is already processed, return cached result
                self.processing_jobs[job_id] = {
                    "status": "completed",
                    "progress": 100,
                    "total_frames": 0,
                    "processed_frames": 0,
                    "filename": cached_filename,
                    "filepath": os.path.join(self.output_dir, cached_filename),
                    "cached": True
                }
                return os.path.join(self.output_dir, cached_filename)
            
            # Initialize job status
            self.processing_jobs[job_id] = {
                "status": "processing",
                "progress": 0,
                "total_frames": 0,
                "processed_frames": 0,
                "filename": None,
                "error": None,
                "cached": False
            }
            
            # Open video
            cap = cv2.VideoCapture(video_url)
            if not cap.isOpened():
                raise Exception("Could not open video")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Update job with total frames
            self.processing_jobs[job_id]["total_frames"] = total_frames
            
            # Create output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_{filter_type}_{timestamp}.mp4"
            filepath = os.path.join(self.output_dir, filename)
            
            # Initialize video writer with XVID codec (more compatible)
            temp_filepath = filepath.replace('.mp4', '_temp.avi')
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(temp_filepath, fourcc, fps, (width, height))
            
            if not video_writer.isOpened():
                raise Exception("Could not create output video")
            
            # Process frames
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply background filter
                processed_frame = apply_background_filter(frame, filter_type)
                
                # Write processed frame
                video_writer.write(processed_frame)
                
                # Update progress
                frame_count += 1
                progress = (frame_count / total_frames) * 100
                self.processing_jobs[job_id].update({
                    "progress": round(progress, 1),
                    "processed_frames": frame_count
                })
                
                # Add small delay to prevent overwhelming the system
                time.sleep(0.01)
            
            # Clean up
            cap.release()
            video_writer.release()
            
            # Convert to MP4 with H.264 codec and preserve original audio using ffmpeg
            try:
                import subprocess
                # First, extract audio from original video
                audio_filepath = filepath.replace('.mp4', '_audio.aac')
                audio_cmd = [
                    'ffmpeg', '-i', video_url, 
                    '-vn', '-acodec', 'aac', '-y', audio_filepath
                ]
                subprocess.run(audio_cmd, check=True, capture_output=True)
                
                # Then combine processed video with original audio
                cmd = [
                    'ffmpeg', '-i', temp_filepath, '-i', audio_filepath,
                    '-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', 
                    '-crf', '23', '-shortest', '-y', filepath
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Clean up temporary audio file
                if os.path.exists(audio_filepath):
                    os.remove(audio_filepath)
                
                # Remove temporary file
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                    
            except Exception as e:
                logger.error(f"Error converting video: {e}")
                # If conversion fails, use the original file
                if os.path.exists(temp_filepath):
                    os.rename(temp_filepath, filepath)
            
            # Add to cache
            self.add_to_cache(video_url, filter_type, filename)
            
            # Update job status
            self.processing_jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "filename": filename,
                "filepath": filepath
            })
            
            return filepath
            
        except Exception as e:
            # Update job with error
            self.processing_jobs[job_id].update({
                "status": "error",
                "error": str(e)
            })
            raise e
    
    def get_job_status(self, job_id):
        """
        Get status of a processing job
        """
        return self.processing_jobs.get(job_id, None)
    
    def list_processed_videos(self):
        """
        List all processed videos
        """
        if not os.path.exists(self.output_dir):
            return []
        
        videos = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.mp4'):
                filepath = os.path.join(self.output_dir, filename)
                file_size = os.path.getsize(filepath)
                
                # Check if this video is in cache
                is_cached = any(filename == cached_filename for cached_filename in self.cache_index.values())
                
                videos.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size": file_size,
                    "downloadUrl": f"/processed-video/download/{filename}",
                    "cached": is_cached
                })
        
        return videos
    
    def clear_cache(self):
        """
        Clear all cached videos and cache index
        """
        try:
            # Remove all cached video files
            for filename in self.cache_index.values():
                filepath = os.path.join(self.output_dir, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            # Clear cache index
            self.cache_index = {}
            self.save_cache()
            
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_cache_info(self):
        """
        Get cache statistics
        """
        total_cached = len(self.cache_index)
        total_size = 0
        
        for filename in self.cache_index.values():
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
        
        return {
            "total_cached_videos": total_cached,
            "total_cache_size_bytes": total_size,
            "total_cache_size_mb": round(total_size / (1024 * 1024), 2)
        }

# Global video processor instance
video_processor = VideoProcessor()

def start_video_processing(video_url, filter_type):
    """
    Start processing a video in background thread
    """
    job_id = f"job_{int(time.time())}"
    
    # Start processing in background thread
    thread = threading.Thread(
        target=video_processor.process_video,
        args=(video_url, filter_type, job_id)
    )
    thread.daemon = True
    thread.start()
    
    return job_id

def get_processing_status(job_id):
    """
    Get status of video processing job
    """
    return video_processor.get_job_status(job_id)

def get_processed_videos():
    """
    Get list of processed videos
    """
    return video_processor.list_processed_videos()

def clear_cache():
    """
    Clear all cached videos
    """
    return video_processor.clear_cache()

def get_cache_info():
    """
    Get cache statistics
    """
    return video_processor.get_cache_info()

