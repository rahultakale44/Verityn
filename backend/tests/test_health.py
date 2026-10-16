"""Tests for health check endpoint."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    """Test that health response has the documented schema."""
    response = client.get("/api/v1/health")
    data = response.json()
    
    # Check required fields exist
    assert "app_name" in data
    assert "status" in data
    assert "version" in data
    
    # Check field types
    assert isinstance(data["app_name"], str)
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    
    # Check expected values
    assert data["app_name"] == "Verityn"
    assert data["status"] == "healthy"
    assert data["version"] == "0.4.0"


def test_health_endpoint_works_without_mongodb(client):
    """Test that health endpoint works without MongoDB connection."""
    # This test verifies that the health endpoint doesn't crash
    # even if MongoDB is not available
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
