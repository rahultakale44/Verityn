"""Tests for ICP management."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from bson import ObjectId
from app.models.icp import ICPCreate, ICPUpdate, ICPResponse
from app.db.icps import (
    create_icp,
    get_icp,
    list_icps,
    update_icp,
    delete_icp,
    ICPNotFoundError
)


@pytest.fixture
def mock_collection():
    """Mock MongoDB collection."""
    return Mock()


@pytest.fixture
def sample_icp_data():
    """Sample ICP creation data."""
    return ICPCreate(
        name="Enterprise SaaS Companies",
        description="Target enterprise SaaS companies in North America",
        industries=["Software", "Technology", "SaaS"],
        headquarters_countries=["United States", "Canada"],
        minimum_employee_count=100,
        maximum_employee_count=5000,
        required_keywords=["enterprise", "B2B", "cloud"],
        excluded_keywords=["consumer", "B2C"],
        criteria_weights={
            "industry": 20.0,
            "headquarters_country": 15.0,
            "employee_count": 25.0,
            "required_keywords": 30.0,
            "excluded_keywords": 10.0
        },
        qualification_threshold=70.0,
        partial_qualification_threshold=50.0,
        minimum_evidence_coverage=60.0
    )


def test_create_icp(mock_collection, sample_icp_data):
    """Test creating an ICP."""
    mock_id = ObjectId()
    mock_collection.insert_one.return_value.inserted_id = mock_id
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        result = create_icp(sample_icp_data)
        
        assert result.id == str(mock_id)
        assert result.name == "Enterprise SaaS Companies"
        assert result.industries == ["Software", "Technology", "SaaS"]
        assert result.qualification_threshold == 70.0
        assert mock_collection.insert_one.called


def test_create_icp_with_defaults():
    """Test creating an ICP with default values."""
    icp = ICPCreate(
        name="Minimal ICP"
    )
    
    assert icp.name == "Minimal ICP"
    assert icp.description is None
    assert icp.industries is None
    assert icp.criteria_weights["industry"] == 20.0
    assert icp.qualification_threshold == 70.0


def test_create_icp_invalid_name():
    """Test that blank ICP name is rejected."""
    with pytest.raises(ValueError, match="cannot be empty"):
        ICPCreate(name="   ")


def test_create_icp_invalid_employee_range():
    """Test that invalid employee range is rejected."""
    with pytest.raises(ValueError, match="cannot be less than minimum"):
        ICPCreate(
            name="Test ICP",
            minimum_employee_count=1000,
            maximum_employee_count=500
        )


def test_create_icp_negative_weight():
    """Test that negative weights are rejected."""
    with pytest.raises(ValueError, match="cannot be negative"):
        ICPCreate(
            name="Test ICP",
            criteria_weights={"industry": -10.0}
        )


def test_create_icp_invalid_thresholds():
    """Test that invalid threshold ordering is rejected."""
    with pytest.raises(ValueError, match="cannot be greater than"):
        ICPCreate(
            name="Test ICP",
            qualification_threshold=50.0,
            partial_qualification_threshold=70.0
        )


def test_get_icp(mock_collection):
    """Test retrieving an ICP by ID."""
    mock_id = ObjectId()
    now = datetime.now(timezone.utc)
    
    mock_collection.find_one.return_value = {
        "_id": mock_id,
        "name": "Test ICP",
        "description": "Test description",
        "industries": ["Technology"],
        "headquarters_countries": ["United States"],
        "minimum_employee_count": 100,
        "maximum_employee_count": 1000,
        "required_keywords": ["enterprise"],
        "excluded_keywords": ["consumer"],
        "criteria_weights": {
            "industry": 20.0,
            "headquarters_country": 15.0,
            "employee_count": 25.0,
            "required_keywords": 30.0,
            "excluded_keywords": 10.0
        },
        "qualification_threshold": 70.0,
        "partial_qualification_threshold": 50.0,
        "minimum_evidence_coverage": 60.0,
        "created_at": now,
        "updated_at": now
    }
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        result = get_icp(str(mock_id))
        
        assert result.id == str(mock_id)
        assert result.name == "Test ICP"
        assert result.industries == ["Technology"]


def test_get_icp_not_found(mock_collection):
    """Test retrieving a non-existent ICP."""
    mock_collection.find_one.return_value = None
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        with pytest.raises(ICPNotFoundError):
            get_icp(str(ObjectId()))


def test_get_icp_invalid_id(mock_collection):
    """Test retrieving an ICP with invalid ID format."""
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        with pytest.raises(ValueError, match="Invalid ICP ID format"):
            get_icp("invalid-id")


def test_list_icps(mock_collection):
    """Test listing ICPs."""
    mock_id1 = ObjectId()
    mock_id2 = ObjectId()
    now = datetime.now(timezone.utc)
    
    mock_collection.count_documents.return_value = 2
    mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
        {
            "_id": mock_id1,
            "name": "ICP 1",
            "description": None,
            "industries": None,
            "headquarters_countries": None,
            "minimum_employee_count": None,
            "maximum_employee_count": None,
            "required_keywords": None,
            "excluded_keywords": None,
            "criteria_weights": {"industry": 20.0},
            "qualification_threshold": 70.0,
            "partial_qualification_threshold": 50.0,
            "minimum_evidence_coverage": 60.0,
            "created_at": now,
            "updated_at": now
        },
        {
            "_id": mock_id2,
            "name": "ICP 2",
            "description": None,
            "industries": None,
            "headquarters_countries": None,
            "minimum_employee_count": None,
            "maximum_employee_count": None,
            "required_keywords": None,
            "excluded_keywords": None,
            "criteria_weights": {"industry": 20.0},
            "qualification_threshold": 70.0,
            "partial_qualification_threshold": 50.0,
            "minimum_evidence_coverage": 60.0,
            "created_at": now,
            "updated_at": now
        }
    ]
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        icps, total = list_icps(limit=50, offset=0)
        
        assert total == 2
        assert len(icps) == 2
        assert icps[0].name == "ICP 1"
        assert icps[1].name == "ICP 2"


def test_update_icp(mock_collection):
    """Test updating an ICP."""
    mock_id = ObjectId()
    now = datetime.now(timezone.utc)
    
    mock_collection.find_one_and_update.return_value = {
        "_id": mock_id,
        "name": "Updated ICP Name",
        "description": "Updated description",
        "industries": ["Technology"],
        "headquarters_countries": None,
        "minimum_employee_count": None,
        "maximum_employee_count": None,
        "required_keywords": None,
        "excluded_keywords": None,
        "criteria_weights": {"industry": 25.0},
        "qualification_threshold": 75.0,
        "partial_qualification_threshold": 50.0,
        "minimum_evidence_coverage": 60.0,
        "created_at": now,
        "updated_at": now
    }
    
    update_data = ICPUpdate(
        name="Updated ICP Name",
        description="Updated description",
        criteria_weights={"industry": 25.0},
        qualification_threshold=75.0
    )
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        result = update_icp(str(mock_id), update_data)
        
        assert result.name == "Updated ICP Name"
        assert result.criteria_weights["industry"] == 25.0
        assert result.qualification_threshold == 75.0


def test_update_icp_not_found(mock_collection):
    """Test updating a non-existent ICP."""
    mock_collection.find_one_and_update.return_value = None
    
    update_data = ICPUpdate(name="New Name")
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        with pytest.raises(ICPNotFoundError):
            update_icp(str(ObjectId()), update_data)


def test_delete_icp(mock_collection):
    """Test deleting an ICP."""
    mock_id = ObjectId()
    mock_collection.delete_one.return_value.deleted_count = 1
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        delete_icp(str(mock_id))
        
        mock_collection.delete_one.assert_called_once()


def test_delete_icp_not_found(mock_collection):
    """Test deleting a non-existent ICP."""
    mock_collection.delete_one.return_value.deleted_count = 0
    
    with patch('app.db.icps.get_icps_collection', return_value=mock_collection):
        with pytest.raises(ICPNotFoundError):
            delete_icp(str(ObjectId()))
