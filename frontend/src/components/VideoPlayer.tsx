import React, { useState, useRef, useEffect } from 'react';
import type { VideoItem } from '../App';

interface VideoPlayerProps {
  video: VideoItem;
  onClose: () => void;
  onProcess: (filterType: string) => Promise<void>;
  isProcessing?: boolean;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ video, onClose, onProcess, isProcessing = false }) => {
  console.log('VideoPlayer: Received video:', video);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('grayscale');
  const videoRef = useRef<HTMLVideoElement>(null);

  // Monitor video URL changes
  useEffect(() => {
    console.log('VideoPlayer: Video URL changed to:', video.url);
    if (videoRef.current) {
      videoRef.current.load(); // Force reload when URL changes
    }
  }, [video.url]);

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleProcessVideo = async () => {
    await onProcess(selectedFilter);
  };

  const testVideoUrl = async () => {
    try {
      console.log('Testing video URL:', video.url);
      const response = await fetch(video.url, { method: 'HEAD' });
      console.log('Video URL test response:', response.status, response.headers);
    } catch (error) {
      console.error('Video URL test error:', error);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-player-overlay" onClick={() => setShowControls(!showControls)}>
      <div className="video-player" onClick={(e) => e.stopPropagation()}>
        <div className="video-container">
          {!isProcessing && (
            <video
              ref={videoRef}
              src={video.url}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onError={(e) => {
                console.error('Video error:', e);
                console.error('Video error details:', videoRef.current?.error);
              }}
              onLoadStart={() => console.log('Video loading started:', video.url)}
              onCanPlay={() => console.log('Video can play:', video.url)}
              onLoadedData={() => console.log('Video loaded data:', video.url)}
              onStalled={() => console.log('Video stalled:', video.url)}
              onSuspend={() => console.log('Video suspended:', video.url)}
              className="video-element"
              crossOrigin="anonymous"
              preload="auto"
              controls
            />
          )}
          
          {isProcessing && (
            <div className="processing-placeholder">
              <div className="processing-content">
                <h2>Processing Video</h2>
                <p>Applying background filter...</p>
                <div className="processing-spinner">⏳</div>
              </div>
            </div>
          )}
          
          {showControls && (
            <div className="video-controls">
              <div className="controls-top">
                <button className="close-btn" onClick={onClose}>✕</button>
                <h2 className="video-title">{video.title}</h2>
              </div>
              
              <div className="controls-center">
                <button className="play-btn" onClick={handlePlayPause}>
                  {isPlaying ? '⏸️' : '▶️'}
                </button>
              </div>
              
              <div className="controls-bottom">
                <div className="progress-bar">
                  <input
                    type="range"
                    min="0"
                    max={duration}
                    value={currentTime}
                    onChange={handleSeek}
                    className="progress-slider"
                  />
                  <div className="time-display">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                </div>
                
                {!isProcessing && (
                  <div className="processing-controls" onClick={(e) => e.stopPropagation()}>
                    <button 
                      className="process-btn"
                      onClick={() => handleProcessVideo(selectedFilter)}
                    >
                      🎬 Process Video
                    </button>
                    <button 
                      className="test-btn"
                      onClick={testVideoUrl}
                      style={{ background: '#6c757d', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      🔍 Test URL
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        <div className="video-info-panel">
          <h3>{video.title}</h3>
          <p>{video.description}</p>
          <div className="video-meta">
            <span>Duration: {video.duration}</span>
            <span>Category: {video.category}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer; 