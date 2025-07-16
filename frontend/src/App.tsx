import React, { useState, useEffect } from 'react';
import './App.css';
import VideoPlayer from './components/VideoPlayer';
import { getProxiedVideoUrl } from './utils/videoUtils';

export interface VideoItem {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  url: string;
  duration: string;
  category: 'featured' | 'recent' | 'processed' | 'grayscale' | 'sepia' | 'blur';
  filterType?: string;
}

const App: React.FC = () => {
  const [currentVideo, setCurrentVideo] = useState<VideoItem | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingJob, setProcessingJob] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<any>(null);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processedVideoUrl, setProcessedVideoUrl] = useState<string | null>(null);
  const [showCustomPrompt, setShowCustomPrompt] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    const loadVideos = async () => {
      try {
        setIsLoading(true);
        const { videoUrls } = await import('./utils/videoUtils');
        
        // Create video grid with filter-specific cards
        const videoItems: VideoItem[] = [
          {
            id: 'grayscale-filter',
            title: 'Grayscale Background',
            description: 'Convert background to grayscale while keeping people in color',
            thumbnail: '/api/thumbnail?url=' + encodeURIComponent(videoUrls[0].url),
            url: getProxiedVideoUrl(videoUrls[0].url),
            duration: '2:30',
            category: 'grayscale',
            filterType: 'grayscale'
          },
          {
            id: 'sepia-filter',
            title: 'Sepia Tone Effect',
            description: 'Apply vintage sepia tone to background',
            thumbnail: '/api/thumbnail?url=' + encodeURIComponent(videoUrls[0].url),
            url: getProxiedVideoUrl(videoUrls[0].url),
            duration: '2:30',
            category: 'sepia',
            filterType: 'sepia'
          },
          {
            id: 'blur-filter',
            title: 'Blur Background',
            description: 'Blur the background while keeping people sharp',
            thumbnail: '/api/thumbnail?url=' + encodeURIComponent(videoUrls[0].url),
            url: getProxiedVideoUrl(videoUrls[0].url),
            duration: '2:30',
            category: 'blur',
            filterType: 'blur'
          }
        ];
        
        setVideos(videoItems);
      } catch (error) {
        console.error('Error loading videos:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadVideos();
  }, []);

  const handleVideoSelect = async (video: VideoItem) => {
    // Start processing immediately when video is clicked
    setIsProcessing(true);
    setCurrentVideo(video);
    
    try {
      const response = await fetch('http://127.0.0.1:8080/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          videoUrl: video.url,
          filterType: video.filterType || 'grayscale' // Use the filter type from the card
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setProcessingJob(data.jobId);
      } else {
        console.error('Failed to start processing');
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Error starting processing:', error);
      setIsProcessing(false);
    }
  };

  const handleProcessVideo = async (filterType: string) => {
    if (!currentVideo) return;
    
    setIsProcessing(true);
    try {
      const response = await fetch('http://127.0.0.1:8080/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          videoUrl: currentVideo.url,
          filterType: filterType
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setProcessingJob(data.jobId);
      } else {
        throw new Error('Failed to start processing');
      }
    } catch (error) {
      console.error('Error starting processing:', error);
      setIsProcessing(false);
    }
  };

  const handleCloseVideo = () => {
    setCurrentVideo(null);
  };

  const handleProcessingComplete = () => {
    setIsProcessing(false);
    setProcessingJob(null);
    setProcessingStatus(null);
    setProcessedVideoUrl(null);
  };

  // Poll for processing status
  useEffect(() => {
    if (!processingJob || !isProcessing) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8080/processing-status/${processingJob}`);
        if (response.ok) {
          const status = await response.json();
          setProcessingStatus(status);
          
          if (status.status === 'completed') {
            // Processing is done, show the processed video
            const processedUrl = `http://127.0.0.1:8080/processed-video/stream/${status.filename}`;
            handlePlayProcessedVideo(processedUrl);
          } else if (status.status === 'error') {
            console.error('Processing error:', status.error);
            setIsProcessing(false);
          }
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    };

    const interval = setInterval(pollStatus, 1000); // Poll every second
    return () => clearInterval(interval);
  }, [processingJob, isProcessing]);



  const handlePlayProcessedVideo = (videoUrl: string) => {
    console.log('Playing processed video:', videoUrl);
    setProcessedVideoUrl(videoUrl);
    setIsProcessing(false);
    setProcessingJob(null);
    
    // Create a processed video item
    const processedVideo: VideoItem = {
      id: 'processed-video',
      title: 'Processed Video',
      description: 'Your video with background filter applied',
      thumbnail: '/api/thumbnail?url=' + encodeURIComponent(videoUrl),
      url: videoUrl,
      duration: 'Processed',
      category: 'processed'
    };
    
    console.log('Setting current video:', processedVideo);
    setCurrentVideo(processedVideo);
  };

  if (isLoading) {
    return (
      <div className="app">
        <div className="header">
          <h1>Loading...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="header">
        <div className="logo-section">
          <div className="logo">🎬</div>
          <h1>Overlap Studio</h1>
        </div>
        <p className="tagline">AI-Powered Video Background Effects for Content Creators</p>
        <p className="description">
          Transform your videos with intelligent background filtering. Keep your subjects in focus while creating stunning visual effects. Perfect for YouTube, TikTok, Instagram, and professional content.
        </p>
        <div className="header-actions">
          <button 
            className="btn-primary"
            onClick={() => setShowUpload(true)}
          >
            🚀 Start Creating
          </button>
          <button 
            className="btn-secondary"
            onClick={() => setShowCustomPrompt(true)}
          >
            ✨ Custom Effects
          </button>
        </div>
        <div className="features-preview">
          <div className="feature-item">
            <span className="feature-icon">🎯</span>
            <span>Smart Person Detection</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <span>Real-time Processing</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🎨</span>
            <span>Multiple Effects</span>
          </div>
        </div>
      </div>
      
      {currentVideo ? (
        <VideoPlayer 
          video={currentVideo}
          onClose={handleCloseVideo}
          onProcess={handleProcessVideo}
          isProcessing={isProcessing}
        />
      ) : (
        <div className="video-grid">
          {videos.map((video) => (
            <div 
              key={video.id} 
              className="video-card" 
              data-category={video.category}
              onClick={() => handleVideoSelect(video)}
            >
              <div className="video-thumbnail">
                📹 {video.title}
              </div>
              <div className="video-info">
                <h3>{video.title}</h3>
                <p>{video.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>📁 Upload Your Video</h2>
              <button className="close-btn" onClick={() => setShowUpload(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="upload-area">
                <div className="upload-icon">📹</div>
                <h3>Drop your video here</h3>
                <p>or click to browse files</p>
                <input 
                  type="file" 
                  accept="video/*" 
                  className="file-input"
                  onChange={(e) => {
                    console.log('File selected:', e.target.files?.[0]);
                    setShowUpload(false);
                  }}
                />
              </div>
              <div className="upload-info">
                <p><strong>Supported formats:</strong> MP4, MOV, AVI</p>
                <p><strong>Max size:</strong> 100MB</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Custom Effect Modal */}
      {showCustomPrompt && (
        <div className="modal-overlay">
          <div className="modal-content custom-effect-modal">
            <div className="modal-header">
              <h2>✨ Create Custom Effect</h2>
              <button className="close-btn" onClick={() => setShowCustomPrompt(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="prompt-section">
                <label htmlFor="effect-prompt">
                  <span className="label-icon">💭</span>
                  Describe your custom background effect:
                </label>
                <textarea 
                  id="effect-prompt"
                  placeholder="Examples:
• 'Transform the background into a sunset beach with palm trees'
• 'Apply a cyberpunk neon city effect with glowing lights'
• 'Make it look like a cozy coffee shop interior'
• 'Create a futuristic space station background'
• 'Turn it into a lush forest with sunlight filtering through trees'"
                  rows={6}
                  className="prompt-textarea"
                  autoFocus
                />
                <div className="prompt-tips">
                  <p><strong>💡 Tips:</strong> Be specific about colors, mood, and style. The more detailed your description, the better the result!</p>
                </div>
              </div>
              
              <div className="effect-preview">
                <h4>
                  <span className="preview-icon">🎨</span>
                  Effect Preview
                </h4>
                <div className="preview-placeholder">
                  <div className="preview-content">
                    <div className="preview-image">✨</div>
                    <p>Your custom effect will be generated here</p>
                    <small>Based on your prompt description</small>
                  </div>
                </div>
              </div>
              
              <div className="action-buttons">
                <button className="btn-primary generate-btn">
                  <span className="btn-icon">🚀</span>
                  Generate Custom Effect
                </button>
                <button className="btn-secondary" onClick={() => setShowCustomPrompt(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {isProcessing && processingJob && (
        <div className="processing-modal">
          <div className="processing-content">
            <h2>Processing Video</h2>
            <p>Applying background filter...</p>
            
            {processingStatus && (
              <>
                <div className="progress-text">
                  {processingStatus.progress ? `${processingStatus.progress}%` : 'Starting...'}
                </div>
                
                <div className="progress-bar-container">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${processingStatus.progress || 0}%` 
                    }}
                  ></div>
                </div>
                
                <div className="frame-count">
                  {processingStatus.processed_frames && processingStatus.total_frames ? (
                    `Frame ${processingStatus.processed_frames} of ${processingStatus.total_frames}`
                  ) : (
                    'Initializing...'
                  )}
                </div>
              </>
            )}
            
            <div className="action-buttons">
              <button className="btn-secondary" onClick={handleProcessingComplete}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
