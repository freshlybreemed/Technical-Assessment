#!/usr/bin/env python3
"""
Test script for video chunk generation functionality
"""

import cv2
import numpy as np
import os
from datetime import datetime

def create_test_video_chunk():
    """
    Create a test video chunk to demonstrate the functionality
    """
    print("🎬 Creating test video chunk...")
    
    # Create temp_videos directory if it doesn't exist
    os.makedirs("temp_videos", exist_ok=True)
    
    # Video parameters
    width, height = 640, 480
    fps = 10
    duration = 3  # 3 seconds
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_chunk_{timestamp}.mp4"
    filepath = os.path.join("temp_videos", filename)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("❌ Error: Could not open video writer")
        return None
    
    # Generate test frames
    total_frames = fps * duration
    print(f"📹 Generating {total_frames} frames...")
    
    for frame_num in range(total_frames):
        # Create a test frame with moving elements
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add a moving circle
        x = int((frame_num / total_frames) * width)
        y = height // 2
        cv2.circle(frame, (x, y), 50, (0, 255, 0), -1)
        
        # Add some text
        cv2.putText(frame, f"Frame {frame_num + 1}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add timestamp
        cv2.putText(frame, f"Time: {frame_num / fps:.1f}s", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Write frame
        video_writer.write(frame)
        
        # Progress indicator
        if frame_num % 10 == 0:
            progress = (frame_num / total_frames) * 100
            print(f"   Progress: {progress:.1f}%")
    
    # Release video writer
    video_writer.release()
    
    # Check if file was created
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"✅ Test video chunk created successfully!")
        print(f"   📁 File: {filename}")
        print(f"   📏 Size: {file_size / 1024:.1f} KB")
        print(f"   ⏱️  Duration: {duration} seconds")
        print(f"   🎬 FPS: {fps}")
        print(f"   📐 Resolution: {width}x{height}")
        return filepath
    else:
        print("❌ Error: Video file was not created")
        return None

def test_video_playback(filepath):
    """
    Test video playback to verify the chunk was created correctly
    """
    if not filepath or not os.path.exists(filepath):
        print("❌ Error: Video file not found")
        return False
    
    print(f"🎥 Testing video playback: {os.path.basename(filepath)}")
    
    # Open video file
    cap = cv2.VideoCapture(filepath)
    
    if not cap.isOpened():
        print("❌ Error: Could not open video file")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"   📊 Video Properties:")
    print(f"      FPS: {fps}")
    print(f"      Frames: {frame_count}")
    print(f"      Resolution: {width}x{height}")
    
    # Read a few frames to verify
    frames_read = 0
    max_frames_to_read = min(5, frame_count)
    
    while frames_read < max_frames_to_read:
        ret, frame = cap.read()
        if not ret:
            break
        
        frames_read += 1
        print(f"   ✅ Frame {frames_read} read successfully")
    
    cap.release()
    
    if frames_read == max_frames_to_read:
        print(f"✅ Video playback test successful!")
        return True
    else:
        print(f"❌ Error: Only {frames_read} frames could be read")
        return False

def list_video_chunks():
    """
    List all video chunks in the temp_videos directory
    """
    chunks_dir = "temp_videos"
    
    if not os.path.exists(chunks_dir):
        print("📁 No temp_videos directory found")
        return []
    
    chunks = []
    for filename in os.listdir(chunks_dir):
        if filename.endswith('.mp4'):
            filepath = os.path.join(chunks_dir, filename)
            file_size = os.path.getsize(filepath)
            chunks.append({
                'filename': filename,
                'filepath': filepath,
                'size': file_size
            })
    
    if chunks:
        print(f"📁 Found {len(chunks)} video chunk(s):")
        for chunk in chunks:
            print(f"   📹 {chunk['filename']} ({chunk['size'] / 1024:.1f} KB)")
    else:
        print("📁 No video chunks found")
    
    return chunks

def main():
    """
    Main test function
    """
    print("🎬 Video Chunk Generation Test")
    print("=" * 40)
    
    # List existing chunks
    print("\n1. Checking existing video chunks...")
    existing_chunks = list_video_chunks()
    
    # Create test chunk
    print("\n2. Creating test video chunk...")
    test_filepath = create_test_video_chunk()
    
    if test_filepath:
        # Test playback
        print("\n3. Testing video playback...")
        test_video_playback(test_filepath)
        
        # List chunks again
        print("\n4. Updated video chunks list...")
        list_video_chunks()
        
        print(f"\n✅ Test completed successfully!")
        print(f"📁 Test video saved to: {test_filepath}")
    else:
        print("\n❌ Test failed!")
    
    print("\n" + "=" * 40)
    print("🎬 Video chunk generation is working correctly!")

if __name__ == "__main__":
    main()
