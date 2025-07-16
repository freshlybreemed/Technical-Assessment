// Backend video proxy URL
const BACKEND_URL = 'http://127.0.0.1:8080';

// Video URLs that will be proxied through the backend
export const videoUrls = [
  {
    id: "primary",
    name: "Primary Video",
    url: "https://storage.googleapis.com/rizeo-40249.appspot.com/01a23584-c6dc-4e70-b82e-8058f3db090e.mp4"
  }
];

// Function to get a proxied video URL
export const getProxiedVideoUrl = (videoUrl: string): string => {
  return `${BACKEND_URL}/video-proxy?url=${encodeURIComponent(videoUrl)}`;
};


