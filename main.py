from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import secrets
from typing import Optional
import logging
from database import Database
from database import Database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Radha API", version="1.0")

# Enhanced CORS configuration for production compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily to troubleshoot
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PUT", "PATCH"],  # Allow all common methods
    allow_headers=["*"],  # Allow all headers to simplify configuration
    expose_headers=["*"],  # Expose all headers
    max_age=3600  # Longer cache for preflight requests (1 hour)
)

# Initialize database
db = Database()

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files directory mounted")
except Exception as e:
    logger.error(f"Failed to mount static files: {str(e)}")

# Create a default API key
DEFAULT_API_KEY = os.environ.get("DEFAULT_API_KEY")
if not DEFAULT_API_KEY:
    DEFAULT_API_KEY = secrets.token_urlsafe(32)
    logger.info(f"Generated new default API key: {DEFAULT_API_KEY[:5]}...")
else:
    logger.info(f"Using default API key from environment: {DEFAULT_API_KEY[:5]}...")

# Store default API key in database if it's connected
if db.connected:
    db.store_api_key(DEFAULT_API_KEY, {"is_default": True})
    logger.info("Default API key stored in database")
else:
    # Fallback to in-memory storage if database isn't connected
    VALID_API_KEYS = set([DEFAULT_API_KEY])
    logger.warning("Database not connected, using in-memory API key storage")

print(f"Default API Key: {DEFAULT_API_KEY}")

# Auth header checker
def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    # Try database validation first
    if db.connected:
        is_valid = db.validate_api_key(token)
    else:
        # Fallback to in-memory validation
        is_valid = token in VALID_API_KEYS
    
    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return token

@app.get("/")
async def dashboard():
    return FileResponse("index.html")

@app.get("/test_api.html")
async def test_api():
    return FileResponse("test_api.html")

@app.get("/health")
async def health():
    # Check database connectivity
    db_status = "connected" if db.connected else "disconnected"
    return {
        "status": "healthy", 
        "service": "radha-api", 
        "domain": "www.radhaapi.me",
        "database": db_status
    }

@app.get("/status")
async def status_page():
    return FileResponse("static/status.html")

@app.get("/server-status")
async def detailed_status_page():
    return FileResponse("static/server-status.html")

@app.get("/api")
async def api_root():
    return {"message": "Radha API running", "key": DEFAULT_API_KEY}

# Enhanced OPTIONS handler with better compatibility
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    # Log the OPTIONS request for debugging
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"OPTIONS request for /{full_path} from {client_host}")
    logger.info(f"OPTIONS headers: {dict(request.headers)}")
    
    # Return with comprehensive CORS headers
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",  # Allow all headers for maximum compatibility
            "Access-Control-Max-Age": "3600",     # 1 hour cache for preflight
            "Access-Control-Allow-Credentials": "true",
            "Vary": "Origin",                     # Important for caching with different origins
            "Content-Length": "0"                 # Explicitly set content length for OPTIONS
        }
    )

@app.post("/generate-api-key")
async def generate_api(request: Request):
    try:
        # Log request details for debugging
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Generate API key requested from: {client_host}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Generate new API key
        new_key = secrets.token_urlsafe(32)
        
        # Store in database if connected
        if db.connected:
            metadata = {
                "ip": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "origin": request.headers.get("origin", "unknown")
            }
            db.store_api_key(new_key, metadata)
            logger.info(f"New API key stored in database: {new_key[:5]}...")
        else:
            # Fallback to in-memory storage
            VALID_API_KEYS.add(new_key)
            logger.info(f"New API key added to in-memory storage: {new_key[:5]}...")
        
        # Return with explicit CORS headers to ensure browser compatibility
        return JSONResponse(
            status_code=200,
            content={"api_key": new_key, "message": "API key generated"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Max-Age": "3600",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"Error in generate_api: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate API key: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )

# GET method as a fallback for API key generation (useful when POST has CORS issues)
@app.get("/generate-api-key-temp")
async def generate_api_temp(request: Request):
    try:
        # Log request details for debugging
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"GET API key generation requested from: {client_host}")
        
        new_key = secrets.token_urlsafe(32)
        
        # Store in database if connected
        if db.connected:
            metadata = {
                "ip": client_host,
                "user_agent": request.headers.get("user-agent", "unknown"),
                "origin": request.headers.get("origin", "unknown"),
                "method": "GET"  # Note this was generated via GET method
            }
            db.store_api_key(new_key, metadata)
            logger.info(f"New API key stored in database via GET: {new_key[:5]}...")
        else:
            # Fallback to in-memory storage
            VALID_API_KEYS.add(new_key)
            logger.info(f"New API key added to in-memory storage via GET: {new_key[:5]}...")
        
        # Return with enhanced CORS headers
        return JSONResponse(
            status_code=200,
            content={"api_key": new_key, "message": "API key generated via GET fallback"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate" # Prevent caching
            }
        )
    except Exception as e:
        logger.error(f"Error in generate_api_temp: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate API key: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

@app.get("/list-api-keys")
async def list_keys(_: str = Depends(verify_api_key)):
    if db.connected:
        api_keys = db.get_all_api_keys()
        return {"total": len(api_keys), "api_keys": api_keys, "storage": "mongodb"}
    else:
        return {"total": len(VALID_API_KEYS), "api_keys": list(VALID_API_KEYS), "storage": "memory"}

@app.get("/get-audio")
async def get_audio(query: str, _: str = Depends(verify_api_key)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query is empty")

    import requests
    
    # Use a simpler approach to fetch results
    logger.info(f"Searching for: {query}")
    
    try:
        # First, search for the video
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        response = requests.get(search_url, headers=headers)
        response_text = response.text
        
        # Extract video ID from search results
        import re
        video_ids = re.findall(r"watch\?v=(\S{11})", response_text)
        
        if not video_ids:
            logger.error("No videos found in search results")
            raise HTTPException(status_code=404, detail="No videos found for query: " + query)
            
        video_id = video_ids[0]
        logger.info(f"Found video ID: {video_id}")
        
        # Get video title and details
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_response = requests.get(video_url, headers=headers)
        
        # Extract title
        title_match = re.search(r'<title>(.*?) - YouTube</title>', video_response.text)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # Create direct URLs for audio and thumbnail
        audio_url = f"https://music.youtube.com/watch?v={video_id}"  # YouTube Music URL that clients can process
        thumbnail = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        
        # Estimate duration (we don't have exact duration but clients can handle this)
        duration = 240  # Default 4 minutes
        
        logger.info(f"Title: {title}")
        logger.info(f"Audio URL: {audio_url}")
        
        return {
            "title": title,
            "duration": duration,
            "audio_url": audio_url,
            "thumbnail": thumbnail,
            "video_id": video_id  # Adding video_id for client-side processing
        }
        
    except Exception as e:
        logger.error(f"Error fetching song: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch song: {str(e)}")

# Add a diagnostic endpoint to help troubleshoot API issues
@app.get("/debug-info")
async def debug_info(request: Request):
    try:
        # Collect information about the environment
        import sys
        import platform
        
        client_host = request.client.host if request.client else "unknown"
        
        # Get API keys count from database or fallback to in-memory
        if db.connected:
            api_keys = db.get_all_api_keys()
            api_keys_count = len(api_keys)
            storage_type = "mongodb"
        else:
            api_keys_count = len(VALID_API_KEYS)
            storage_type = "memory"
            
        debug_data = {
            "server_info": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "environment": {k: v for k, v in os.environ.items() if k.lower() in 
                              ['port', 'host', 'railway_static_url', 'railway_environment', 
                               'python_env', 'path', 'server_software']},
                "domain": "www.radhaapi.me",
            },
            "request_info": {
                "client_ip": client_host,
                "headers": dict(request.headers),
                "method": request.method,
                "url": str(request.url),
                "host": request.headers.get("host", "unknown"),
            },
            "cors_config": {
                "allow_origins": "*",
                "allow_methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
            },
            "api_keys": {
                "total_keys": api_keys_count,
                "default_key_length": len(DEFAULT_API_KEY) if DEFAULT_API_KEY else 0,
                "storage_type": storage_type,
                "database_connected": db.connected
            }
        }
        
        logger.info(f"Debug info accessed by {client_host}")
        return JSONResponse(content=debug_data)
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error generating debug info: {str(e)}"}
        )

@app.get("/test")
async def test_dashboard():
    return FileResponse("index_local.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))  # Changed default port to 8002
    uvicorn.run(app, host="0.0.0.0", port=port)
