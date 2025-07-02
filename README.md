# Radha API - YouTube Audio API for Music Bots

A specialized API for extracting audio information from YouTube videos, designed specifically for music bots and similar applications.

## Features

- 🎵 Fetch audio URLs from YouTube using simple search queries
- 🔐 API key authentication for secure access
- 💾 MongoDB integration for persistent API key storage
- 🌐 CORS support for browser-based applications
- 📊 Detailed status and debugging endpoints

## Live API

The API is deployed and accessible at:
- https://www.radhaapi.me

## Quick Start

### Using the API

1. Get the default API key from the root endpoint:
   ```
   GET https://www.radhaapi.me/api
   ```

2. Use the API key to search for audio:
   ```
   GET https://www.radhaapi.me/get-audio?query=your+search+query
   ```
   Include the API key in the Authorization header:
   ```
   Authorization: Bearer YOUR_API_KEY
   ```

3. Parse the response:
   ```json
   {
     "title": "Song title",
     "duration": 240,
     "audio_url": "https://music.youtube.com/watch?v=VIDEO_ID",
     "thumbnail": "https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg",
     "video_id": "VIDEO_ID"
   }
   ```

### Local Development

1. Clone the repository
   ```
   git clone https://github.com/yourusername/radha-api.git
   cd radha-api
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up MongoDB (optional)
   - Install MongoDB or use MongoDB Atlas
   - Set the `MONGODB_URI` environment variable to your MongoDB connection string

4. Run the server
   ```
   python main.py
   ```

5. Access the local API at http://localhost:8002

## API Documentation

### Endpoints

- `GET /` - Web dashboard
- `GET /api` - Get default API key
- `GET /generate-api-key-temp` - Generate a new API key
- `GET /get-audio?query=SEARCH_QUERY` - Get audio info by search query
- `GET /health` - Check API health status
- `GET /server-status` - Detailed server status page

## Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## MongoDB Integration

This project uses MongoDB to store API keys persistently. When the MongoDB connection is available, API keys are stored and validated from the database. If MongoDB is not available, the application falls back to in-memory storage for API keys.

### Setup

1. Create a MongoDB Atlas account or install MongoDB locally
2. Set the `MONGODB_URI` environment variable to your MongoDB connection string
3. (Optional) Set the `DEFAULT_API_KEY` environment variable to specify a default API key

## Tech Stack

- FastAPI - Web framework
- MongoDB - Database for API key storage
- yt-dlp - YouTube video information extraction
- Uvicorn - ASGI server
- Railway - Deployment platform

## License

[MIT License](LICENSE)
