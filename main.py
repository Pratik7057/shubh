from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import secrets
from typing import Optional
import logging
import asyncio
import aiohttp
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Radha API", version="1.0")

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Create a default API key
DEFAULT_API_KEY = os.environ.get("DEFAULT_API_KEY", "Q1qiNovI299UOHscCiKfvgODwo9Xjr_R3c2Cuzk3sL4")
VALID_API_KEYS = set([DEFAULT_API_KEY])

print(f"Default API Key: {DEFAULT_API_KEY}")

# Auth verification for query parameter
def verify_api_key_query(api: str = Query(...)):
    if api not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api

# Auth verification for Bearer token
def verify_api_key_bearer(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    if token not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return token

@app.get("/")
async def dashboard():
    return {"message": "Radha API running", "key": DEFAULT_API_KEY}

@app.get("/api")
async def api_root():
    return {"message": "Radha API running", "key": DEFAULT_API_KEY}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "radha-api", "domain": "web-production-3c26.up.railway.app"}

# NEW: Bot-compatible endpoint
@app.get("/api/song/{video_id}")
async def get_song_by_id(video_id: str, api: str = Depends(verify_api_key_query)):
    """Bot-compatible endpoint: /api/song/{video_id}?api={API_KEY}"""
    try:
        logger.info(f"Fetching song for video ID: {video_id}")
        
        # Download the song using yt-dlp
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)
        
        # Check if file already exists
        for ext in ["mp3", "m4a", "webm"]:
            file_path = f"{download_folder}/{video_id}.{ext}"
            if os.path.exists(file_path):
                logger.info(f"File already exists: {file_path}")
                return {
                    "status": "done",
                    "format": ext,
                    "link": f"https://web-production-3c26.up.railway.app/download/{video_id}.{ext}"
                }
        
        # Download using yt-dlp
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_folder}/%(id)s.%(ext)s',
            'extractaudio': True,
            'audioformat': 'mp3',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Extract info first
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                # Download the audio
                ydl.download([video_url])
                
                # Find the downloaded file
                for ext in ["mp3", "m4a", "webm"]:
                    file_path = f"{download_folder}/{video_id}.{ext}"
                    if os.path.exists(file_path):
                        return {
                            "status": "done",
                            "title": title,
                            "duration": duration,
                            "format": ext,
                            "link": f"https://web-production-3c26.up.railway.app/download/{video_id}.{ext}"
                        }
                
                return {"status": "error", "message": "Download failed"}
                
            except Exception as e:
                logger.error(f"yt-dlp error: {str(e)}")
                return {"status": "error", "message": f"Download failed: {str(e)}"}
        
    except Exception as e:
        logger.error(f"Error in get_song_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process song: {str(e)}")

# File download endpoint
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"downloads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='audio/mpeg'
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Original get-audio endpoint (Bearer token auth)
@app.get("/get-audio")
async def get_audio(query: str, _: str = Depends(verify_api_key_bearer)):
    """Original endpoint: /get-audio?query={search_query} with Bearer token"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query is empty")

    try:
        # Search for the video
        import requests
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        
        response = requests.get(search_url, headers=headers)
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        
        if not video_ids:
            raise HTTPException(status_code=404, detail="No videos found")
            
        video_id = video_ids[0]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get video details
        video_response = requests.get(video_url, headers=headers)
        title_match = re.search(r'<title>(.*?) - YouTube</title>', video_response.text)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        audio_url = f"https://music.youtube.com/watch?v={video_id}"
        thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        
        return {
            "title": title,
            "duration": 240,
            "audio_url": audio_url,
            "thumbnail": thumbnail,
            "video_id": video_id
        }
        
    except Exception as e:
        logger.error(f"Error fetching song: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch song: {str(e)}")

# API key generation endpoints
@app.get("/generate-api-key-temp")
async def generate_api_temp():
    new_key = secrets.token_urlsafe(32)
    VALID_API_KEYS.add(new_key)
    return {"api_key": new_key, "message": "API key generated"}

@app.post("/generate-api-key")
async def generate_api():
    new_key = secrets.token_urlsafe(32)
    VALID_API_KEYS.add(new_key)
    return {"api_key": new_key, "message": "API key generated"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
