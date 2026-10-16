"""Saved views data access layer."""
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.db.mongodb import mongodb
from app.db.companies import DatabaseConnectionError
from app.models.saved_view import (
    SavedViewResponse,
    SavedViewFilters
)


class SavedViewNotFoundError(Exception):
    """Raised when a saved view is not found."""
    pass


def get_saved_views_collection():
    """Get the saved_views collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.saved_views


def ensure_saved_views_indexes():
    """
    Create necessary indexes for the saved_views collection.
    
    Creates indexes for:
    - created_at descending for listing (newest first)
    """
    try:
        collection = get_saved_views_collection()
        
        collection.create_index(
            [("created_at", -1)],
            name="created_at_desc"
        )
        
    except PyMongoError:
        pass


def filters_to_dict(filters: SavedViewFilters) -> dict:
    """Convert SavedViewFilters to dict for storage."""
    return {
        "icp_id": filters.icp_id,
        "outcomes": filters.outcomes,
        "min_score": filters.min_score,
        "max_score": filters.max_score,
        "min_evidence_coverage": filters.min_evidence_coverage,
        "industries": filters.industries,
        "countries": filters.countries,
        "min_employees": filters.min_employees,
        "max_employees": filters.max_employees,
        "company_name_search": filters.company_name_search,
        "has_research": filters.has_research,
        "sort_by": filters.sort_by,
        "sort_direction": filters.sort_direction
    }


def dict_to_filters(data: dict) -> SavedViewFilters:
    """Convert dict to SavedViewFilters."""
    return SavedViewFilters(**data)


def document_to_response(doc: dict) -> SavedViewResponse:
    """
    Convert MongoDB document to SavedViewResponse.
    
    Args:
        doc: MongoDB document
        
    Returns:
        SavedViewResponse model
    """
    return SavedViewResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        filters=dict_to_filters(doc["filters"]),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )


def create_saved_view(
    name: str,
    filters: SavedViewFilters,
    description: Optional[str] = None
) -> SavedViewResponse:
    """
    Create a new saved view.
    
    Args:
        name: View name
        filters: Filter configuration
        description: Optional description
        
    Returns:
        Created saved view
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_saved_views_collection()
    
    now = datetime.now(timezone.utc)
    
    doc = {
        "name": name,
        "description": description,
        "filters": filters_to_dict(filters),
        "created_at": now,
        "updated_at": now
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    return document_to_response(doc)


def get_saved_view(view_id: str) -> SavedViewResponse:
    """
    Get a saved view by ID.
    
    Args:
        view_id: Saved view ID
        
    Returns:
        Saved view record
        
    Raises:
        SavedViewNotFoundError: If saved view does not exist
        ValueError: If view_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_saved_views_collection()
    
    try:
        object_id = ObjectId(view_id)
    except Exception:
        raise ValueError(f"Invalid saved view ID format: {view_id}")
    
    doc = collection.find_one({"_id": object_id})
    
    if doc is None:
        raise SavedViewNotFoundError(f"Saved view with ID {view_id} not found")
    
    return document_to_response(doc)


def list_saved_views(
    limit: int = 50,
    offset: int = 0
) -> tuple[list[SavedViewResponse], int]:
    """
    List saved views.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of saved views, total count)
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_saved_views_collection()
    
    # Get total count
    total = collection.count_documents({})
    
    # Get paginated results, sorted by created_at descending (newest first)
    cursor = collection.find({}).sort("created_at", -1).skip(offset).limit(limit)
    
    views = [document_to_response(doc) for doc in cursor]
    
    return views, total


def update_saved_view(
    view_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    filters: Optional[SavedViewFilters] = None
) -> SavedViewResponse:
    """
    Update a saved view.
    
    Args:
        view_id: Saved view ID
        name: Optional new name
        description: Optional new description
        filters: Optional new filter configuration
        
    Returns:
        Updated saved view
        
    Raises:
        SavedViewNotFoundError: If saved view does not exist
        ValueError: If view_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_saved_views_collection()
    
    try:
        object_id = ObjectId(view_id)
    except Exception:
        raise ValueError(f"Invalid saved view ID format: {view_id}")
    
    # Build update document
    update_doc = {
        "updated_at": datetime.now(timezone.utc)
    }
    
    if name is not None:
        update_doc["name"] = name
    
    if description is not None:
        update_doc["description"] = description
    
    if filters is not None:
        update_doc["filters"] = filters_to_dict(filters)
    
    # Update document
    result = collection.find_one_and_update(
        {"_id": object_id},
        {"$set": update_doc},
        return_document=True
    )
    
    if result is None:
        raise SavedViewNotFoundError(f"Saved view with ID {view_id} not found")
    
    return document_to_response(result)


def delete_saved_view(view_id: str) -> None:
    """
    Delete a saved view.
    
    Args:
        view_id: Saved view ID
        
    Raises:
        SavedViewNotFoundError: If saved view does not exist
        ValueError: If view_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_saved_views_collection()
    
    try:
        object_id = ObjectId(view_id)
    except Exception:
        raise ValueError(f"Invalid saved view ID format: {view_id}")
    
    result = collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise SavedViewNotFoundError(f"Saved view with ID {view_id} not found")
