from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database connection and operations class"""
    
    def __init__(self):
        """Initialize database connection"""
        self.client = None
        self.db = None
        self.api_keys = None
        self.connected = False
        self.connect()

    def connect(self):
        """Connect to MongoDB database"""
        try:
            # Get MongoDB URI from environment variable or use default for local development
            mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/radhaapi")
            
            # Connect to MongoDB
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Check connection
            self.client.server_info()
            
            # Get database (last part of the URI path or default to 'radhaapi')
            db_name = mongo_uri.split('/')[-1] if '/' in mongo_uri else 'radhaapi'
            self.db = self.client[db_name]
            
            # Get collections
            self.api_keys = self.db['api_keys']
            
            # Create index on API key for faster lookups
            self.api_keys.create_index('key', unique=True)
            
            self.connected = True
            logger.info(f"Connected to MongoDB: {db_name}")
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            self.connected = False
    
    def store_api_key(self, key, metadata=None):
        """Store a new API key in the database"""
        if not self.connected:
            logger.warning("Cannot store API key: Database not connected")
            return False
        
        try:
            # Prepare document
            document = {
                "key": key,
                "created_at": datetime.datetime.utcnow(),
                "is_active": True
            }
            
            # Add metadata if provided
            if metadata:
                document["metadata"] = metadata
                
            # Insert document
            result = self.api_keys.insert_one(document)
            logger.info(f"API key stored with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store API key: {str(e)}")
            return False
    
    def validate_api_key(self, key):
        """Check if an API key exists and is active"""
        if not self.connected:
            logger.warning("Cannot validate API key: Database not connected")
            return False
            
        try:
            result = self.api_keys.find_one({"key": key, "is_active": True})
            return result is not None
            
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
    
    def get_all_api_keys(self):
        """Get all API keys"""
        if not self.connected:
            logger.warning("Cannot get API keys: Database not connected")
            return []
            
        try:
            keys = list(self.api_keys.find({}, {"key": 1, "_id": 0}))
            return [doc["key"] for doc in keys]
            
        except Exception as e:
            logger.error(f"Failed to get API keys: {str(e)}")
            return []

# Import datetime for document timestamps
import datetime
