/**
 * Haven Production & Development Configuration
 * 
 * Instructions:
 * 1. For Render Backend: Set your Render backend service URL below (e.g., "https://myhaven-backend.onrender.com").
 * 2. For Local Running: Leave BACKEND_URL as "" or set to "http://127.0.0.1:8000". The frontend will automatically detect localhost!
 * 3. For Vercel Serverless: Leave BACKEND_URL as "" to use Vercel's built-in Python API proxy.
 */
window.HAVEN_CONFIG = {
    // Empty BACKEND_URL allows local detection (http://127.0.0.1:8000) or specify directly
    BACKEND_URL: "http://127.0.0.1:8000"
};
