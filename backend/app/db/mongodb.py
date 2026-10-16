"""MongoDB connection management using PyMongo."""
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import settings


class MongoDB:
    """MongoDB client manager with lazy initialization."""
    
    def __init__(self) -> None:
        self._client: Optional[MongoClient] = None
    
    def connect(self) -> None:
        """Initialize MongoDB connection."""
        if self._client is None:
            # Create client with reasonable timeout
            self._client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000
            )
    
    def close(self) -> None:
        """Close MongoDB connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
    
    def get_client(self) -> Optional[MongoClient]:
        """Get the MongoDB client instance."""
        return self._client
    
    def get_database(self):
        """Get the configured database."""
        if self._client is None:
            return None
        return self._client[settings.mongodb_database]
    
    def ping(self) -> bool:
        """
        Test MongoDB connection.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            if self._client is None:
                return False
            # The ping command is a simple way to test connectivity
            self._client.admin.command('ping')
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception):
            return False


# Global MongoDB instance
mongodb = MongoDB()
