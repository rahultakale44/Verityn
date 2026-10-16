"""Tests for research functionality."""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.db.research import (
    normalize_url,
    extract_domain,
    ResearchNotFoundError
)
from app.services.tavily_service import TavilyConfigurationError, TavilySearchError


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_company():
    """Create a mock company."""
    return Mock(
        id="507f1f77bcf86cd799439011",
        company_name="Test Company",
        website="https://example.com",
        industry="Technology",
        headquarters_country="United States",
        headquarters_region="California"
    )


@pytest.fixture
def mock_research_run():
    """Create a mock research run."""
    return Mock(
        id="507f1f77bcf86cd799439012",
        company_id="507f1f77bcf86cd799439011",
        status="completed",
        started_at=datetime(2024, 1, 1, 12, 0, 0),
        completed_at=datetime(2024, 1, 1, 12, 5, 0),
        queries_executed=5,
        sources_found=10,
        sources_saved=8,
        error_summary=None
    )


# Test utility functions
def test_normalize_url():
    """Test URL normalization for deduplication."""
    assert normalize_url("https://Example.com/") == "https://example.com"
    assert normalize_url("HTTPS://EXAMPLE.COM/PATH/") == "https://example.com/path"
    assert normalize_url("https://example.com/path?q=1") == "https://example.com/path?q=1"


def test_extract_domain():
    """Test domain extraction from URLs."""
    assert extract_domain("https://example.com/path") == "example.com"
    assert extract_domain("http://subdomain.example.com") == "subdomain.example.com"
    assert extract_domain("invalid-url") == "invalid-url"


# Test POST /api/v1/companies/{company_id}/research - Start Research
@patch('app.api.routes.research.research_service.conduct_research')
@patch('app.api.routes.research.get_company')
def test_start_research_success(mock_get_company, mock_conduct, client, mock_company, mock_research_run):
    """Test successful research initiation."""
    mock_get_company.return_value = mock_company
    mock_conduct.return_value = mock_research_run
    
    response = client.post("/api/v1/companies/507f1f77bcf86cd799439011/research")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["company_id"] == "507f1f77bcf86cd799439011"
    assert data["queries_executed"] == 5
    assert data["sources_saved"] == 8


@patch('app.api.routes.research.get_company')
def test_start_research_company_not_found(mock_get_company, client):
    """Test research for non-existent company."""
    from app.db.companies import CompanyNotFoundError
    mock_get_company.side_effect = CompanyNotFoundError("Company not found")
    
    response = client.post("/api/v1/companies/507f1f77bcf86cd799439011/research")
    
    assert response.status_code == 404


@patch('app.api.routes.research.get_company')
def test_start_research_invalid_company_id(mock_get_company, client):
    """Test research with invalid company ID."""
    mock_get_company.side_effect = ValueError("Invalid company ID format")
    
    response = client.post("/api/v1/companies/invalid/research")
    
    assert response.status_code == 422


@patch('app.api.routes.research.research_service.conduct_research')
@patch('app.api.routes.research.get_company')
def test_start_research_tavily_not_configured(mock_get_company, mock_conduct, client, mock_company):
    """Test research when Tavily API is not configured."""
    mock_get_company.return_value = mock_company
    mock_conduct.side_effect = TavilyConfigurationError("Tavily API key is not configured")
    
    response = client.post("/api/v1/companies/507f1f77bcf86cd799439011/research")
    
    assert response.status_code == 503
    assert "configured" in response.json()["detail"].lower()


# Test GET /api/v1/companies/{company_id}/research - List Research Runs
@patch('app.api.routes.research.list_research_runs')
def test_list_research_runs_success(mock_list, client, mock_research_run):
    """Test listing research runs for a company."""
    mock_list.return_value = ([mock_research_run], 1)
    
    response = client.get("/api/v1/companies/507f1f77bcf86cd799439011/research")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1


@patch('app.api.routes.research.list_research_runs')
def test_list_research_runs_empty(mock_list, client):
    """Test listing when no research runs exist."""
    mock_list.return_value = ([], 0)
    
    response = client.get("/api/v1/companies/507f1f77bcf86cd799439011/research")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@patch('app.api.routes.research.list_research_runs')
def test_list_research_runs_pagination(mock_list, client):
    """Test research run pagination."""
    mock_list.return_value = ([], 100)
    
    response = client.get("/api/v1/companies/507f1f77bcf86cd799439011/research?limit=10&offset=20")
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 20
    mock_list.assert_called_once_with(
        company_id="507f1f77bcf86cd799439011",
        limit=10,
        offset=20
    )


# Test GET /api/v1/companies/{company_id}/research/{research_run_id} - Get Research Run
@patch('app.api.routes.research.get_research_run')
def test_get_research_run_success(mock_get, client, mock_research_run):
    """Test getting research run details."""
    mock_get.return_value = mock_research_run
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439011/research/507f1f77bcf86cd799439012"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "507f1f77bcf86cd799439012"
    assert data["company_id"] == "507f1f77bcf86cd799439011"


@patch('app.api.routes.research.get_research_run')
def test_get_research_run_not_found(mock_get, client):
    """Test getting non-existent research run."""
    mock_get.side_effect = ResearchNotFoundError("Research run not found")
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439011/research/507f1f77bcf86cd799439012"
    )
    
    assert response.status_code == 404


@patch('app.api.routes.research.get_research_run')
def test_get_research_run_wrong_company(mock_get, client):
    """Test getting research run with wrong company ID."""
    mock_get.side_effect = ResearchNotFoundError("Research run not found for company")
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439999/research/507f1f77bcf86cd799439012"
    )
    
    assert response.status_code == 404


# Test GET /api/v1/companies/{company_id}/research/{research_run_id}/sources - List Sources
@patch('app.api.routes.research.list_source_evidence')
def test_list_sources_success(mock_list, client):
    """Test listing source evidence."""
    mock_source = Mock(
        id="507f1f77bcf86cd799439013",
        research_run_id="507f1f77bcf86cd799439012",
        company_id="507f1f77bcf86cd799439011",
        source_url="https://example.com/article",
        source_domain="example.com",
        title="Test Article",
        snippet="This is a test snippet",
        published_at=None,
        retrieved_at=datetime(2024, 1, 1, 12, 1, 0),
        provider="Tavily",
        content_type=None
    )
    mock_list.return_value = ([mock_source], 1)
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439011/research/507f1f77bcf86cd799439012/sources"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["source_url"] == "https://example.com/article"
    assert data["items"][0]["provider"] == "Tavily"


@patch('app.api.routes.research.list_source_evidence')
def test_list_sources_empty(mock_list, client):
    """Test listing sources when none exist."""
    mock_list.return_value = ([], 0)
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439011/research/507f1f77bcf86cd799439012/sources"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


@patch('app.api.routes.research.list_source_evidence')
def test_list_sources_pagination(mock_list, client):
    """Test source evidence pagination."""
    mock_list.return_value = ([], 50)
    
    response = client.get(
        "/api/v1/companies/507f1f77bcf86cd799439011/research/507f1f77bcf86cd799439012/sources?limit=20&offset=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 20
    assert data["offset"] == 10


# Test Research Service
@patch('app.services.research_service.tavily_service.search')
@patch('app.services.research_service.save_source_evidence')
@patch('app.services.research_service.update_research_run')
@patch('app.services.research_service.create_research_run')
def test_research_service_conduct_research(
    mock_create, mock_update, mock_save, mock_search, mock_company
):
    """Test research service conducts research correctly."""
    from app.services.research_service import research_service
    
    # Mock research run creation
    mock_run = Mock(id="507f1f77bcf86cd799439012")
    mock_create.return_value = mock_run
    mock_update.return_value = mock_run
    
    # Mock Tavily search results
    mock_search.return_value = {
        "results": [
            {
                "url": "https://example.com/article1",
                "title": "Article 1",
                "content": "This is article 1 content"
            },
            {
                "url": "https://example.com/article2",
                "title": "Article 2",
                "content": "This is article 2 content"
            }
        ]
    }
    
    # Mock save evidence
    mock_save.return_value = Mock(id="507f1f77bcf86cd799439013")
    
    # Conduct research
    result = research_service.conduct_research(mock_company)
    
    # Verify research run was created
    mock_create.assert_called_once_with(mock_company.id)
    
    # Verify searches were executed
    assert mock_search.call_count > 0
    
    # Verify sources were saved
    assert mock_save.call_count > 0


@patch('app.services.research_service.tavily_service.search')
@patch('app.services.research_service.update_research_run')
@patch('app.services.research_service.create_research_run')
def test_research_service_handles_search_errors(
    mock_create, mock_update, mock_search, mock_company
):
    """Test research service handles search errors gracefully."""
    from app.services.research_service import research_service
    
    mock_run = Mock(id="507f1f77bcf86cd799439012")
    mock_create.return_value = mock_run
    mock_update.return_value = mock_run
    
    # Mock search failure
    mock_search.side_effect = TavilySearchError("Search failed")
    
    # Conduct research (should handle errors)
    result = research_service.conduct_research(mock_company)
    
    # Verify final status was updated (should be failed or partial)
    assert mock_update.call_count >= 2  # At least running and final status


@patch('app.services.research_service.update_research_run')
@patch('app.services.research_service.create_research_run')
def test_research_service_tavily_not_configured(mock_create, mock_update, mock_company):
    """Test research service when Tavily is not configured."""
    from app.services.research_service import research_service
    
    mock_run = Mock(id="507f1f77bcf86cd799439012")
    mock_create.return_value = mock_run
    mock_update.return_value = mock_run
    
    # Mock Tavily configuration error
    with patch('app.services.research_service.tavily_service.search') as mock_search:
        mock_search.side_effect = TavilyConfigurationError("API key not configured")
        
        with pytest.raises(TavilyConfigurationError):
            research_service.conduct_research(mock_company)


def test_generate_search_queries(mock_company):
    """Test search query generation."""
    from app.services.research_service import research_service
    
    queries = research_service.generate_search_queries(mock_company)
    
    assert len(queries) > 0
    assert len(queries) <= 5  # Bounded to 5 queries
    assert any(mock_company.company_name in q for q in queries)


def test_generate_search_queries_minimal_info():
    """Test query generation with minimal company info."""
    from app.services.research_service import research_service
    
    minimal_company = Mock(
        company_name="Minimal Corp",
        website=None,
        industry=None,
        headquarters_country=None,
        headquarters_region=None
    )
    
    queries = research_service.generate_search_queries(minimal_company)
    
    assert len(queries) >= 1
    assert "Minimal Corp" in queries[0]


# Test Tavily Service
def test_tavily_service_is_configured():
    """Test Tavily configuration check."""
    from app.services.tavily_service import tavily_service
    
    # Should return False with placeholder key
    with patch('app.services.tavily_service.settings.tavily_api_key', 'your_tavily_api_key_here'):
        assert tavily_service.is_configured() is False
    
    # Should return True with real-looking key
    with patch('app.services.tavily_service.settings.tavily_api_key', 'tvly-abc123'):
        assert tavily_service.is_configured() is True


def test_tavily_service_search_not_configured():
    """Test Tavily search when not configured."""
    from app.services.tavily_service import tavily_service
    
    with patch('app.services.tavily_service.settings.tavily_api_key', ''):
        with pytest.raises(TavilyConfigurationError):
            tavily_service.search("test query")
