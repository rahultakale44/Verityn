"""ICP data access layer."""
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.db.mongodb import mongodb
from app.db.companies import DatabaseConnectionError
from app.models.icp import ICPCreate, ICPUpdate, ICPResponse


class ICPNotFoundError(Exception):
    """Raised when an ICP is not found."""
    pass


def get_icps_collection():
    """Get the icps collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.icps


def ensure_icp_indexes():
    """
    Create necessary indexes for the icps collection.
    
    Creates:
    - Index on created_at for sorting
    - Index on name for searching
    """
    try:
        collection = get_icps_collection()
        
        collection.create_index(
            [("created_at", -1)],
            name="created_at_desc"
        )
        
        collection.create_index(
            [("name", 1)],
            name="name_idx"
        )
        
    except PyMongoError:
        pass


def document_to_response(doc: dict) -> ICPResponse:
    """
    Convert MongoDB document to ICPResponse.
    
    Args:
        doc: MongoDB document
        
    Returns:
        ICPResponse model
    """
    return ICPResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        industries=doc.get("industries"),
        headquarters_countries=doc.get("headquarters_countries"),
        minimum_employee_count=doc.get("minimum_employee_count"),
        maximum_employee_count=doc.get("maximum_employee_count"),
        required_keywords=doc.get("required_keywords"),
        excluded_keywords=doc.get("excluded_keywords"),
        criteria_weights=doc["criteria_weights"],
        qualification_threshold=doc["qualification_threshold"],
        partial_qualification_threshold=doc["partial_qualification_threshold"],
        minimum_evidence_coverage=doc["minimum_evidence_coverage"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )


def create_icp(icp: ICPCreate) -> ICPResponse:
    """
    Create a new ICP configuration.
    
    Args:
        icp: ICP creation data
        
    Returns:
        Created ICP
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_icps_collection()
    
    now = datetime.now(timezone.utc)
    
    doc = {
        "name": icp.name,
        "description": icp.description,
        "industries": icp.industries,
        "headquarters_countries": icp.headquarters_countries,
        "minimum_employee_count": icp.minimum_employee_count,
        "maximum_employee_count": icp.maximum_employee_count,
        "required_keywords": icp.required_keywords,
        "excluded_keywords": icp.excluded_keywords,
        "criteria_weights": icp.criteria_weights,
        "qualification_threshold": icp.qualification_threshold,
        "partial_qualification_threshold": icp.partial_qualification_threshold,
        "minimum_evidence_coverage": icp.minimum_evidence_coverage,
        "created_at": now,
        "updated_at": now
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    return document_to_response(doc)


def get_icp(icp_id: str) -> ICPResponse:
    """
    Get an ICP by ID.
    
    Args:
        icp_id: ICP ID
        
    Returns:
        ICP record
        
    Raises:
        ICPNotFoundError: If ICP does not exist
        ValueError: If icp_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_icps_collection()
    
    try:
        object_id = ObjectId(icp_id)
    except Exception:
        raise ValueError(f"Invalid ICP ID format: {icp_id}")
    
    doc = collection.find_one({"_id": object_id})
    if doc is None:
        raise ICPNotFoundError(f"ICP with ID {icp_id} not found")
    
    return document_to_response(doc)


def list_icps(limit: int = 50, offset: int = 0) -> tuple[list[ICPResponse], int]:
    """
    List ICPs with pagination.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of ICPs, total count)
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_icps_collection()
    
    # Get total count
    total = collection.count_documents({})
    
    # Get paginated results, sorted by created_at descending (newest first)
    cursor = collection.find().sort("created_at", -1).skip(offset).limit(limit)
    
    icps = [document_to_response(doc) for doc in cursor]
    
    return icps, total


def update_icp(icp_id: str, update_data: ICPUpdate) -> ICPResponse:
    """
    Update an ICP configuration.
    
    Args:
        icp_id: ICP ID
        update_data: Fields to update
        
    Returns:
        Updated ICP record
        
    Raises:
        ICPNotFoundError: If ICP does not exist
        ValueError: If icp_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_icps_collection()
    
    try:
        object_id = ObjectId(icp_id)
    except Exception:
        raise ValueError(f"Invalid ICP ID format: {icp_id}")
    
    # Build update document with only provided fields
    update_doc = {}
    
    if update_data.name is not None:
        update_doc["name"] = update_data.name
    
    if update_data.description is not None:
        update_doc["description"] = update_data.description
    
    if update_data.industries is not None:
        update_doc["industries"] = update_data.industries
    
    if update_data.headquarters_countries is not None:
        update_doc["headquarters_countries"] = update_data.headquarters_countries
    
    if update_data.minimum_employee_count is not None:
        update_doc["minimum_employee_count"] = update_data.minimum_employee_count
    
    if update_data.maximum_employee_count is not None:
        update_doc["maximum_employee_count"] = update_data.maximum_employee_count
    
    if update_data.required_keywords is not None:
        update_doc["required_keywords"] = update_data.required_keywords
    
    if update_data.excluded_keywords is not None:
        update_doc["excluded_keywords"] = update_data.excluded_keywords
    
    if update_data.criteria_weights is not None:
        update_doc["criteria_weights"] = update_data.criteria_weights
    
    if update_data.qualification_threshold is not None:
        update_doc["qualification_threshold"] = update_data.qualification_threshold
    
    if update_data.partial_qualification_threshold is not None:
        update_doc["partial_qualification_threshold"] = update_data.partial_qualification_threshold
    
    if update_data.minimum_evidence_coverage is not None:
        update_doc["minimum_evidence_coverage"] = update_data.minimum_evidence_coverage
    
    if not update_doc:
        # No fields to update, just return current record
        return get_icp(icp_id)
    
    # Add timestamp
    update_doc["updated_at"] = datetime.now(timezone.utc)
    
    result = collection.find_one_and_update(
        {"_id": object_id},
        {"$set": update_doc},
        return_document=True
    )
    
    if result is None:
        raise ICPNotFoundError(f"ICP with ID {icp_id} not found")
    
    return document_to_response(result)


def delete_icp(icp_id: str) -> None:
    """
    Delete an ICP configuration.
    
    Note: This does NOT delete historical qualification results that reference
    this ICP. Those results preserve an immutable snapshot of the ICP configuration.
    
    Args:
        icp_id: ICP ID
        
    Raises:
        ICPNotFoundError: If ICP does not exist
        ValueError: If icp_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_icps_collection()
    
    try:
        object_id = ObjectId(icp_id)
    except Exception:
        raise ValueError(f"Invalid ICP ID format: {icp_id}")
    
    result = collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise ICPNotFoundError(f"ICP with ID {icp_id} not found")
