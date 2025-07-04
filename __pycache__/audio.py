from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Auth header checker - this will use the same logic as main.py
def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    API key verification function for the audio routes
    This will be overridden by the dependency injection from main.py
    """
    from database import Database
    import os
    import secrets
    
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    # Try database validation first
    db = Database()
    if db.connected:
        is_valid = db.validate_api_key(token)
    else:
        # Fallback to checking against default API key
        DEFAULT_API_KEY = os.environ.get("DEFAULT_API_KEY")
        if not DEFAULT_API_KEY:
            DEFAULT_API_KEY = secrets.token_urlsafe(32)
        is_valid = token == DEFAULT_API_KEY
    
    if not is_valid:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return token

def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format
    YouTube video IDs are typically 11 characters long and contain alphanumeric characters, hyphens, and underscores
    """
    if not video_id:
        return False
    
    # YouTube video ID pattern: 11 characters, alphanumeric + - and _
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))

@router.get("/get-stream")
async def get_stream(video_id: Optional[str] = None, _: str = Depends(verify_api_key)):
    """
    Get streaming URL for a YouTube video ID
    
    Args:
        video_id: YouTube video ID (11 characters)
        
    Returns:
        JSON response with stream URL or error message
    """
    
    # Validate video_id parameter
    if not video_id:
        logger.warning("Missing video_id parameter in get-stream request")
        raise HTTPException(
            status_code=400, 
            detail="Missing required parameter: video_id"
        )
    
    if not validate_video_id(video_id):
        logger.warning(f"Invalid video_id format: {video_id}")
        raise HTTPException(
            status_code=400, 
            detail="Invalid video_id format. Expected 11-character YouTube video ID"
        )
    
    # Log the request for debugging
    logger.info(f"Stream requested for video_id: {video_id}")
    
    # Mock streaming URL response
    # In a real implementation, this would generate actual streaming URLs
    stream_url = f"https://web-production-3c26.up.railway.app/stream/{video_id}"
    
    response_data = {
        "status": "success",
        "stream_url": stream_url
    }
    
    logger.info(f"Returning stream URL for video_id {video_id}: {stream_url}")
    
    return response_data
