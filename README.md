# 🎬 Overlap Studio - AI Video Background Effects

A professional video background filtering system that processes entire videos to apply stunning background effects while keeping people in full color. Built for content creators on YouTube, TikTok, Instagram, and professional platforms.

## ✨ Features

### 🎨 **Complete Video Processing**
- **Full Video Processing**: Process entire videos, not just real-time frames
- **Background Effects**: Grayscale, Sepia, and Blur effects
- **Person Detection**: AI-powered person detection using OpenCV
- **Audio Preservation**: Maintains original audio in processed videos
- **High Quality Output**: Professional-grade video processing

### 🎯 **Smart Person Detection**
- **Face Detection**: Haar Cascade classifiers for accurate face detection
- **Body Detection**: Full-body detection for complete person coverage
- **Smooth Masking**: Morphological operations and Gaussian blur for natural edges
- **Intelligent Blending**: Seamless integration of effects with person preservation

### 🚀 **Professional Workflow**
- **Filter Selection**: Choose from pre-built effects or create custom ones
- **Background Processing**: Non-blocking video processing with progress tracking
- **Caching System**: Intelligent caching to avoid re-processing
- **Download Ready**: Processed videos ready for immediate use

### 🎨 **Custom Effects**
- **Text Prompts**: Describe custom effects in natural language
- **AI Generation**: Generate unique background effects from descriptions
- **Effect Preview**: Visual preview of custom effects before processing

## 🏗️ Architecture

### Backend (Python Flask)
- **Computer Vision**: OpenCV for person detection and image processing
- **Video Processing**: Complete video processing with background segmentation
- **Audio Handling**: FFmpeg integration for audio preservation
- **Caching**: Intelligent caching system for processed videos
- **API Endpoints**: RESTful API for video processing and management

### Frontend (React TypeScript + Vite)
- **Modern UI**: Professional dark mode interface with Hinge-like design
- **Filter Cards**: Visual filter selection with effect previews
- **Progress Tracking**: Real-time processing progress with frame counts
- **Responsive Design**: Mobile-optimized interface
- **Video Player**: Full-featured video player with custom controls

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- FFmpeg (for audio processing)

### Backend Setup
```bash
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173 (Vite default)
- **Backend API**: http://localhost:8080

## 📡 API Endpoints

### Video Processing
- `POST /process-video` - Start video processing with background effects
- `GET /processing-status/<job_id>` - Get processing progress
- `GET /processed-videos` - List all processed videos
- `GET /processed-video/stream/<filename>` - Stream processed video

### Video Management
- `GET /video-proxy` - Proxy external video files
- `GET /video-urls` - Get available video sources

### Caching
- `GET /cache/info` - Get cache statistics
- `POST /cache/clear` - Clear all cached videos

## 🎨 Available Effects

| Effect | Description | Visual Style |
|--------|-------------|--------------|
| **Grayscale** | Convert background to black & white | Classic monochrome look |
| **Sepia** | Apply vintage sepia tone | Warm, nostalgic aesthetic |
| **Blur** | Blur background elements | Professional depth of field |
| **Custom** | AI-generated effects from text prompts | Unlimited creative possibilities |

## 🎬 How It Works

### 1. **Select Your Video**
Choose from available demo videos or upload your own

### 2. **Pick Your Effect**
- Select from pre-built effects (Grayscale, Sepia, Blur)
- Or create custom effects with text prompts

### 3. **Process Your Video**
- AI detects people in your video
- Applies effects to background only
- Preserves original audio
- Shows real-time progress

### 4. **Download & Share**
- Get your processed video ready for platforms
- Perfect for YouTube, TikTok, Instagram, and more

## 🔧 Technical Details

### Person Detection Pipeline
```python
def detect_person(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces and bodies
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3)
    bodies = body_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2)
    
    # Create and smooth mask
    mask = create_person_mask(faces, bodies)
    mask = cv2.GaussianBlur(mask, (21, 21), 0)
    
    return mask
```

### Background Filtering Process
1. **Video Input**: Load video with OpenCV
2. **Frame Processing**: Process each frame individually
3. **Person Detection**: Generate person mask for each frame
4. **Effect Application**: Apply selected effect to background
5. **Blending**: Blend person (original) with filtered background
6. **Audio Preservation**: Extract and re-mux original audio
7. **Output**: Generate final MP4 with H.264 codec

### Caching System
```python
def get_cache_key(video_url, filter_type):
    url_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
    return f"{url_hash}_{filter_type}"

def is_cached(self, video_url, filter_type):
    cache_key = self.get_cache_key(video_url, filter_type)
    return cache_key in self.cache_index
```

## 🎯 User Interface

### Main Features:
- **Professional Header**: Overlap Studio branding with animated logo
- **Filter Cards**: Visual effect selection with unique styling
- **Progress Tracking**: Real-time frame count and percentage
- **Video Player**: Full-screen player with custom controls
- **Upload System**: Drag-and-drop video upload interface
- **Custom Effects**: Text prompt interface for AI-generated effects

### Responsive Design:
- **Mobile Optimized**: Touch-friendly interface
- **Dark Mode**: Professional dark theme throughout
- **Smooth Animations**: Hover effects and transitions
- **Accessibility**: Proper contrast and touch targets

## 🚀 Future Enhancements

### Planned Features:
- **Advanced AI Models**: More sophisticated person detection
- **Real-time Processing**: Live video processing capabilities
- **Batch Processing**: Process multiple videos simultaneously
- **Cloud Integration**: Upload to cloud storage platforms
- **Social Media Integration**: Direct posting to platforms

### Performance Optimizations:
- **GPU Acceleration**: CUDA support for faster processing
- **Parallel Processing**: Multi-threaded video processing
- **Smart Caching**: Predictive caching for popular effects
- **CDN Integration**: Global video delivery network

## 🛠️ Troubleshooting

### Common Issues:

#### Video Processing Fails:
- Check FFmpeg installation
- Verify video format compatibility
- Ensure sufficient disk space
- Check backend logs for errors

#### Person Detection Issues:
- Ensure good lighting in video
- Check person visibility and positioning
- Try different filter types
- Verify OpenCV installation

#### Performance Issues:
- Reduce video resolution
- Check system resources
- Use cached videos when possible
- Close other applications

### Debug Endpoints:
- `GET /health` - Check backend status
- `GET /cache/info` - View cache statistics
- `GET /processed-videos` - List processed videos

## 📋 Requirements

### Backend Dependencies:
- Python 3.8+
- OpenCV 4.5+
- Flask 2.0+
- FFmpeg
- NumPy
- Pillow (PIL)

### Frontend Dependencies:
- Node.js 16+
- React 18+
- TypeScript 4.0+
- Vite

### System Requirements:
- 8GB RAM recommended
- 5GB free disk space
- Modern web browser
- FFmpeg installed

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**🎬 Overlap Studio** - Transform your videos with AI-powered background effects. Perfect for content creators who want to stand out on social media platforms.