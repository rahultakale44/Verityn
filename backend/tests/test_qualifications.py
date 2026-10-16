"""Tests for qualification API endpoints."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.qualification import CriterionEvaluation, EvidenceReference


client = TestClient(app)


@pytest.fixture
def mock_company():
    """Mock company response."""
    from app.models.company import CompanyResponse
    
    return CompanyResponse(
        id=str(ObjectId()),
        company_name="Test Company",
        website="https://test.com",
        industry="Software",
        description="Enterprise B2B platform",
        headquarters_country="United States",
        headquarters_region="California",
        employee_count=500,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_icp():
    """Mock ICP response."""
    from app.models.icp import ICPResponse
    
    return ICPResponse(
        id=str(ObjectId()),
        name="Enterprise SaaS",
        description="Target enterprise SaaS",
        industries=["Software"],
        headquarters_countries=["United States"],
        minimum_employee_count=100,
        maximum_employee_count=1000,
        required_keywords=["enterprise", "B2B"],
        excluded_keywords=["consumer"],
        criteria_weights={
            "industry": 20.0,
            "headquarters_country": 15.0,
            "employee_count": 25.0,
            "required_keywords": 30.0,
            "excluded_keywords": 10.0
        },
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_qualification_result():
    """Mock qualification result."""
    from app.models.qualification import QualificationResponse
    
    evaluations = [
        CriterionEvaluation(
            criterion_id="industry",
            criterion_name="Industry Match",
            weight=20.0,
            status="match",
            explanation="Industry matches",
            observed_value="Software",
            expected_value=["Software"]
        )
    ]
    
    return QualificationResponse(
        id=str(ObjectId()),
        company_id=str(ObjectId()),
        icp_id=str(ObjectId()),
        icp_snapshot={},
        qualified_at=datetime.now(timezone.utc),
        score=85.0,
        evidence_coverage=90.0,
        outcome="qualified",
        outcome_explanation="Qualified",
        criteria_evaluations=evaluations,
        limitations="Test limitations"
    )


def test_qualify_company_success(mock_company, mock_icp, mock_qualification_result):
    """Test successful company qualification."""
    with patch('app.api.routes.qualifications.get_company', return_value=mock_company), \
         patch('app.api.routes.qualifications.get_icp', return_value=mock_icp), \
         patch('app.api.routes.qualifications.create_qualification', return_value=mock_qualification_result), \
         patch('app.db.research.get_source_evidence_collection') as mock_sources_collection:
        
        # Mock empty sources
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        mock_sources_collection.return_value.find.return_value = mock_cursor
        
        response = client.post(
            f"/api/v1/companies/{mock_company.id}/qualifications",
            json={"icp_id": mock_icp.id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "outcome" in data
        assert "criteria_evaluations" in data


def test_qualify_company_company_not_found(mock_icp):
    """Test qualification with non-existent company."""
    from app.db.companies import CompanyNotFoundError
    
    with patch('app.api.routes.qualifications.get_company', side_effect=CompanyNotFoundError("Not found")):
        response = client.post(
            f"/api/v1/companies/{str(ObjectId())}/qualifications",
            json={"icp_id": mock_icp.id}
        )
        
        assert response.status_code == 404


def test_qualify_company_icp_not_found(mock_company):
    """Test qualification with non-existent ICP."""
    from app.db.icps import ICPNotFoundError
    
    with patch('app.api.routes.qualifications.get_company', return_value=mock_company), \
         patch('app.api.routes.qualifications.get_icp', side_effect=ICPNotFoundError("Not found")):
        
        response = client.post(
            f"/api/v1/companies/{mock_company.id}/qualifications",
            json={"icp_id": str(ObjectId())}
        )
        
        assert response.status_code == 404


def test_qualify_company_invalid_company_id():
    """Test qualification with invalid company ID."""
    with patch('app.api.routes.qualifications.get_company', side_effect=ValueError("Invalid ID")):
        response = client.post(
            "/api/v1/companies/invalid-id/qualifications",
            json={"icp_id": str(ObjectId())}
        )
        
        assert response.status_code == 422


def test_list_qualifications_success(mock_qualification_result):
    """Test listing qualification history."""
    with patch('app.api.routes.qualifications.list_qualifications', return_value=([mock_qualification_result], 1)):
        company_id = str(ObjectId())
        response = client.get(f"/api/v1/companies/{company_id}/qualifications")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 1


def test_list_qualifications_empty():
    """Test listing qualifications with no results."""
    with patch('app.api.routes.qualifications.list_qualifications', return_value=([], 0)):
        company_id = str(ObjectId())
        response = client.get(f"/api/v1/companies/{company_id}/qualifications")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0


def test_list_qualifications_pagination():
    """Test qualification list pagination."""
    with patch('app.api.routes.qualifications.list_qualifications', return_value=([], 100)):
        company_id = str(ObjectId())
        response = client.get(
            f"/api/v1/companies/{company_id}/qualifications?limit=10&offset=20"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 20


def test_get_qualification_success(mock_qualification_result):
    """Test retrieving a specific qualification."""
    with patch('app.api.routes.qualifications.get_qualification', return_value=mock_qualification_result):
        company_id = str(ObjectId())
        qualification_id = str(ObjectId())
        
        response = client.get(
            f"/api/v1/companies/{company_id}/qualifications/{qualification_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert "criteria_evaluations" in data


def test_get_qualification_not_found():
    """Test retrieving non-existent qualification."""
    from app.db.qualifications import QualificationNotFoundError
    
    with patch('app.api.routes.qualifications.get_qualification', 
               side_effect=QualificationNotFoundError("Not found")):
        company_id = str(ObjectId())
        qualification_id = str(ObjectId())
        
        response = client.get(
            f"/api/v1/companies/{company_id}/qualifications/{qualification_id}"
        )
        
        assert response.status_code == 404


def test_get_qualification_wrong_company():
    """Test retrieving qualification for wrong company."""
    from app.db.qualifications import QualificationNotFoundError
    
    with patch('app.api.routes.qualifications.get_qualification',
               side_effect=QualificationNotFoundError("Qualification not found for company")):
        company_id = str(ObjectId())
        qualification_id = str(ObjectId())
        
        response = client.get(
            f"/api/v1/companies/{company_id}/qualifications/{qualification_id}"
        )
        
        assert response.status_code == 404
