"""Tests for company management functionality."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.main import app
from app.db.companies import (
    CompanyNotFoundError,
    DuplicateCompanyError,
    DatabaseConnectionError,
    normalize_for_comparison,
    normalize_website_for_comparison
)
from app.models.company import CompanyResponse


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_company_response():
    """Create a mock company response."""
    return CompanyResponse(
        id="507f1f77bcf86cd799439011",
        company_name="Test Company",
        website="https://example.com",
        industry="Technology",
        description="A test company",
        headquarters_country="United States",
        headquarters_region="California",
        employee_count=100,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0)
    )


# Test normalization functions
def test_normalize_for_comparison():
    """Test string normalization for duplicate detection."""
    assert normalize_for_comparison("  Test  Company  ") == "test company"
    assert normalize_for_comparison("TEST COMPANY") == "test company"
    assert normalize_for_comparison(None) is None
    assert normalize_for_comparison("") is None


def test_normalize_website_for_comparison():
    """Test website normalization for duplicate detection."""
    assert normalize_website_for_comparison("https://Example.com/") == "https://example.com"
    assert normalize_website_for_comparison("HTTPS://EXAMPLE.COM") == "https://example.com"
    assert normalize_website_for_comparison(None) is None
    assert normalize_website_for_comparison("") is None


# Test POST /api/v1/companies - Create Company
@patch('app.api.routes.companies.create_company')
def test_create_company_success(mock_create, client, mock_company_response):
    """Test successful company creation."""
    mock_create.return_value = mock_company_response
    
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company",
        "website": "https://example.com",
        "industry": "Technology"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Test Company"
    assert data["website"] == "https://example.com"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@patch('app.api.routes.companies.create_company')
def test_create_company_minimal(mock_create, client, mock_company_response):
    """Test company creation with only required fields."""
    mock_create.return_value = mock_company_response
    
    response = client.post("/api/v1/companies", json={
        "company_name": "Minimal Company"
    })
    
    assert response.status_code == 201
    assert response.json()["company_name"] == "Test Company"


def test_create_company_missing_name(client):
    """Test that company name is required."""
    response = client.post("/api/v1/companies", json={
        "website": "https://example.com"
    })
    
    assert response.status_code == 422


def test_create_company_empty_name(client):
    """Test that empty company name is rejected."""
    response = client.post("/api/v1/companies", json={
        "company_name": "   "
    })
    
    assert response.status_code == 422


def test_create_company_invalid_website(client):
    """Test that invalid website URL is rejected."""
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company",
        "website": "not-a-url"
    })
    
    assert response.status_code == 422


def test_create_company_negative_employees(client):
    """Test that negative employee count is rejected."""
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company",
        "employee_count": -10
    })
    
    assert response.status_code == 422


@patch('app.api.routes.companies.create_company')
def test_create_company_duplicate_name(mock_create, client):
    """Test duplicate company name handling."""
    mock_create.side_effect = DuplicateCompanyError(
        "Company with name 'Test Company' already exists",
        "company_name"
    )
    
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company"
    })
    
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]["message"]


@patch('app.api.routes.companies.create_company')
def test_create_company_duplicate_website(mock_create, client):
    """Test duplicate website handling."""
    mock_create.side_effect = DuplicateCompanyError(
        "Company with website 'https://example.com' already exists",
        "website"
    )
    
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company",
        "website": "https://example.com"
    })
    
    assert response.status_code == 409


@patch('app.api.routes.companies.create_company')
def test_create_company_database_unavailable(mock_create, client):
    """Test error when database is unavailable."""
    mock_create.side_effect = DatabaseConnectionError("Database connection not available")
    
    response = client.post("/api/v1/companies", json={
        "company_name": "Test Company"
    })
    
    assert response.status_code == 503


# Test GET /api/v1/companies - List Companies
@patch('app.api.routes.companies.list_companies')
def test_list_companies_success(mock_list, client, mock_company_response):
    """Test successful company listing."""
    mock_list.return_value = ([mock_company_response], 1)
    
    response = client.get("/api/v1/companies")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["company_name"] == "Test Company"


@patch('app.api.routes.companies.list_companies')
def test_list_companies_empty(mock_list, client):
    """Test listing when no companies exist."""
    mock_list.return_value = ([], 0)
    
    response = client.get("/api/v1/companies")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@patch('app.api.routes.companies.list_companies')
def test_list_companies_pagination(mock_list, client):
    """Test company listing with pagination."""
    mock_list.return_value = ([], 100)
    
    response = client.get("/api/v1/companies?limit=10&offset=20")
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 20
    mock_list.assert_called_once_with(limit=10, offset=20)


def test_list_companies_invalid_limit(client):
    """Test that limit above maximum is rejected."""
    response = client.get("/api/v1/companies?limit=1000")
    
    assert response.status_code == 422


def test_list_companies_negative_offset(client):
    """Test that negative offset is rejected."""
    response = client.get("/api/v1/companies?offset=-1")
    
    assert response.status_code == 422


# Test GET /api/v1/companies/{company_id} - Get Company
@patch('app.api.routes.companies.get_company')
def test_get_company_success(mock_get, client, mock_company_response):
    """Test successful company retrieval."""
    mock_get.return_value = mock_company_response
    
    response = client.get("/api/v1/companies/507f1f77bcf86cd799439011")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "507f1f77bcf86cd799439011"
    assert data["company_name"] == "Test Company"


@patch('app.api.routes.companies.get_company')
def test_get_company_not_found(mock_get, client):
    """Test retrieval of non-existent company."""
    mock_get.side_effect = CompanyNotFoundError("Company with ID 507f1f77bcf86cd799439011 not found")
    
    response = client.get("/api/v1/companies/507f1f77bcf86cd799439011")
    
    assert response.status_code == 404


@patch('app.api.routes.companies.get_company')
def test_get_company_invalid_id(mock_get, client):
    """Test retrieval with invalid ObjectId format."""
    mock_get.side_effect = ValueError("Invalid company ID format: invalid")
    
    response = client.get("/api/v1/companies/invalid")
    
    assert response.status_code == 422


# Test PATCH /api/v1/companies/{company_id} - Update Company
@patch('app.api.routes.companies.update_company')
def test_update_company_success(mock_update, client, mock_company_response):
    """Test successful company update."""
    updated_response = mock_company_response.model_copy(update={"industry": "Finance"})
    mock_update.return_value = updated_response
    
    response = client.patch("/api/v1/companies/507f1f77bcf86cd799439011", json={
        "industry": "Finance"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["industry"] == "Finance"


@patch('app.api.routes.companies.update_company')
def test_update_company_multiple_fields(mock_update, client, mock_company_response):
    """Test updating multiple fields."""
    mock_update.return_value = mock_company_response
    
    response = client.patch("/api/v1/companies/507f1f77bcf86cd799439011", json={
        "company_name": "Updated Company",
        "employee_count": 200
    })
    
    assert response.status_code == 200


@patch('app.api.routes.companies.update_company')
def test_update_company_not_found(mock_update, client):
    """Test updating non-existent company."""
    mock_update.side_effect = CompanyNotFoundError("Company with ID 507f1f77bcf86cd799439011 not found")
    
    response = client.patch("/api/v1/companies/507f1f77bcf86cd799439011", json={
        "industry": "Finance"
    })
    
    assert response.status_code == 404


@patch('app.api.routes.companies.update_company')
def test_update_company_duplicate_conflict(mock_update, client):
    """Test update causing duplicate conflict."""
    mock_update.side_effect = DuplicateCompanyError(
        "Company with name 'Existing Company' already exists",
        "company_name"
    )
    
    response = client.patch("/api/v1/companies/507f1f77bcf86cd799439011", json={
        "company_name": "Existing Company"
    })
    
    assert response.status_code == 409


def test_update_company_invalid_data(client):
    """Test update with invalid data."""
    response = client.patch("/api/v1/companies/507f1f77bcf86cd799439011", json={
        "employee_count": -50
    })
    
    assert response.status_code == 422


# Test DELETE /api/v1/companies/{company_id} - Delete Company
@patch('app.api.routes.companies.delete_company')
def test_delete_company_success(mock_delete, client):
    """Test successful company deletion."""
    mock_delete.return_value = None
    
    response = client.delete("/api/v1/companies/507f1f77bcf86cd799439011")
    
    assert response.status_code == 204
    assert response.content == b''


@patch('app.api.routes.companies.delete_company')
def test_delete_company_not_found(mock_delete, client):
    """Test deleting non-existent company."""
    mock_delete.side_effect = CompanyNotFoundError("Company with ID 507f1f77bcf86cd799439011 not found")
    
    response = client.delete("/api/v1/companies/507f1f77bcf86cd799439011")
    
    assert response.status_code == 404


@patch('app.api.routes.companies.delete_company')
def test_delete_company_invalid_id(mock_delete, client):
    """Test deletion with invalid ObjectId."""
    mock_delete.side_effect = ValueError("Invalid company ID format: invalid")
    
    response = client.delete("/api/v1/companies/invalid")
    
    assert response.status_code == 422
