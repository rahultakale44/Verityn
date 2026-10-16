"""Tests for MongoDB connection handling."""
import pytest
from app.db.mongodb import MongoDB


def test_mongodb_ping_handles_failed_connection():
    """Test that database ping helper handles a failed connection safely."""
    # Create a new MongoDB instance without connecting
    db = MongoDB()
    
    # Ping should return False when not connected
    assert db.ping() is False
    
    # Even with a bad connection string, ping should handle it gracefully
    db._client = None
    result = db.ping()
    assert result is False
