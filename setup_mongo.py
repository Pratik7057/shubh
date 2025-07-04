#!/usr/bin/env python
"""
MongoDB connection test script for Radha API
This script tests the connection to MongoDB and creates initial collections
"""

from pymongo import MongoClient
import os
import sys
import logging
import secrets
from pymongo.errors import DuplicateKeyError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test the connection to MongoDB using the MONGODB_URI environment variable"""
    
    # Get MongoDB URI from environment variable
    mongo_uri = os.environ.get("MONGODB_URI")
    if not mongo_uri:
        logger.error("MONGODB_URI environment variable not set")
        print("\nPlease set the MONGODB_URI environment variable. Example:")
        print("export MONGODB_URI='mongodb+srv://username:password@cluster0.mongodb.net/radhaapi'\n")
        return False
    
    try:
        logger.info(f"Connecting to MongoDB using URI: {mongo_uri.split('@')[-1]}")  # Don't log credentials
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Check connection
        server_info = client.server_info()
        logger.info(f"Connected to MongoDB version: {server_info.get('version', 'unknown')}")
        
        # Get database name from URI
        db_name = mongo_uri.split('/')[-1] if '/' in mongo_uri else 'radhaapi'
        db = client[db_name]
        logger.info(f"Using database: {db_name}")
        
        # Check/create collections
        collections = db.list_collection_names()
        logger.info(f"Existing collections: {', '.join(collections) if collections else 'none'}")
        
        # Create api_keys collection if it doesn't exist
        if 'api_keys' not in collections:
            logger.info("Creating api_keys collection")
            db.create_collection('api_keys')
            
            # Create index on key field
            db.api_keys.create_index('key', unique=True)
            logger.info("Created index on api_keys.key field")
        
        else:
            logger.info("api_keys collection already exists")
        
        # Insert default API key only if not exists
        default_key = os.environ.get("DEFAULT_API_KEY") or secrets.token_urlsafe(32)
        existing_key = db.api_keys.find_one({"key": default_key})
        
        if not existing_key:
            try:
                db.api_keys.insert_one({
                    "key": default_key,
                    "is_default": True,
                    "is_active": True
                })
                logger.info(f"Inserted default API key: {default_key[:5]}...")
            except DuplicateKeyError:
                logger.warning("API key already exists in DB (race condition), skipping insert.")
        else:
            logger.warning("Default API key already exists, skipping insert.")
        
        logger.info("MongoDB setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== MongoDB Connection Test for Radha API =====")
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)
