"""Company data access layer."""
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from app.db.mongodb import mongodb
from app.models.company import CompanyCreate, CompanyUpdate, CompanyResponse


class CompanyNotFoundError(Exception):
    """Raised when a company is not found."""
    pass


class DuplicateCompanyError(Exception):
    """Raised when a duplicate company is detected."""
    
    def __init__(self, message: str, field: str):
        super().__init__(message)
        self.field = field


class DatabaseConnectionError(Exception):
    """Raised when database connection is not available."""
    pass


def normalize_for_comparison(value: Optional[str]) -> Optional[str]:
    """
    Normalize string values for duplicate detection.
    
    Args:
        value: String to normalize
        
    Returns:
        Normalized string or None
    """
    if not value:
        return None
    # Convert to lowercase and collapse whitespace
    return ' '.join(str(value).lower().split())


def normalize_website_for_comparison(url: Optional[str]) -> Optional[str]:
    """
    Normalize website URL for duplicate detection.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL or None
    """
    if not url:
        return None
    url_str = str(url).lower().strip()
    # Remove trailing slash
    if url_str.endswith('/'):
        url_str = url_str[:-1]
    return url_str


def get_companies_collection():
    """Get the companies collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.companies


def ensure_indexes():
    """
    Create necessary indexes for the companies collection.
    
    Creates:
    - Unique compound index on normalized_name
    - Unique sparse index on normalized_website
    - Index on created_at for sorting
    """
    try:
        collection = get_companies_collection()
        
        # Unique index on normalized company name
        collection.create_index(
            [("normalized_name", 1)],
            unique=True,
            name="normalized_name_unique"
        )
        
        # Unique sparse index on normalized website (only for non-null values)
        collection.create_index(
            [("normalized_website", 1)],
            unique=True,
            sparse=True,
            name="normalized_website_unique"
        )
        
        # Index for sorting by creation date (newest first)
        collection.create_index(
            [("created_at", -1)],
            name="created_at_desc"
        )
    except PyMongoError:
        # If index creation fails, log but don't crash
        # Indexes might already exist or database might be unavailable
        pass


def document_to_response(doc: dict) -> CompanyResponse:
    """
    Convert MongoDB document to CompanyResponse model.
    
    Args:
        doc: MongoDB document
        
    Returns:
        CompanyResponse model
    """
    return CompanyResponse(
        id=str(doc["_id"]),
        company_name=doc["company_name"],
        website=doc.get("website"),
        industry=doc.get("industry"),
        description=doc.get("description"),
        headquarters_country=doc.get("headquarters_country"),
        headquarters_region=doc.get("headquarters_region"),
        employee_count=doc.get("employee_count"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"]
    )


def create_company(company: CompanyCreate) -> CompanyResponse:
    """
    Create a new company record.
    
    Args:
        company: Company creation data
        
    Returns:
        Created company
        
    Raises:
        DuplicateCompanyError: If company with same name or website exists
        DatabaseConnectionError: If database is not available
    """
    collection = get_companies_collection()
    
    now = datetime.now(timezone.utc)
    
    # Normalize for duplicate detection
    normalized_name = normalize_for_comparison(company.company_name)
    normalized_website = normalize_website_for_comparison(str(company.website) if company.website else None)
    
    doc = {
        "company_name": company.company_name,
        "website": str(company.website) if company.website else None,
        "industry": company.industry,
        "description": company.description,
        "headquarters_country": company.headquarters_country,
        "headquarters_region": company.headquarters_region,
        "employee_count": company.employee_count,
        "normalized_name": normalized_name,
        "normalized_website": normalized_website,
        "created_at": now,
        "updated_at": now
    }
    
    try:
        result = collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return document_to_response(doc)
    except DuplicateKeyError as e:
        # Determine which field caused the duplicate
        if "normalized_name" in str(e):
            raise DuplicateCompanyError(
                f"Company with name '{company.company_name}' already exists",
                "company_name"
            )
        elif "normalized_website" in str(e):
            raise DuplicateCompanyError(
                f"Company with website '{company.website}' already exists",
                "website"
            )
        else:
            raise DuplicateCompanyError("Duplicate company detected", "unknown")


def get_company(company_id: str) -> CompanyResponse:
    """
    Get a company by ID.
    
    Args:
        company_id: Company ID
        
    Returns:
        Company record
        
    Raises:
        CompanyNotFoundError: If company does not exist
        ValueError: If company_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_companies_collection()
    
    try:
        object_id = ObjectId(company_id)
    except Exception:
        raise ValueError(f"Invalid company ID format: {company_id}")
    
    doc = collection.find_one({"_id": object_id})
    if doc is None:
        raise CompanyNotFoundError(f"Company with ID {company_id} not found")
    
    return document_to_response(doc)


def list_companies(limit: int = 50, offset: int = 0) -> tuple[list[CompanyResponse], int]:
    """
    List companies with pagination.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of companies, total count)
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_companies_collection()
    
    # Get total count
    total = collection.count_documents({})
    
    # Get paginated results, sorted by created_at descending (newest first)
    cursor = collection.find().sort("created_at", -1).skip(offset).limit(limit)
    
    companies = [document_to_response(doc) for doc in cursor]
    
    return companies, total


def update_company(company_id: str, update_data: CompanyUpdate) -> CompanyResponse:
    """
    Update a company record.
    
    Args:
        company_id: Company ID
        update_data: Fields to update
        
    Returns:
        Updated company record
        
    Raises:
        CompanyNotFoundError: If company does not exist
        DuplicateCompanyError: If update would create duplicate
        ValueError: If company_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_companies_collection()
    
    try:
        object_id = ObjectId(company_id)
    except Exception:
        raise ValueError(f"Invalid company ID format: {company_id}")
    
    # Build update document with only provided fields
    update_doc = {}
    normalized_updates = {}
    
    if update_data.company_name is not None:
        update_doc["company_name"] = update_data.company_name
        normalized_updates["normalized_name"] = normalize_for_comparison(update_data.company_name)
    
    if update_data.website is not None:
        update_doc["website"] = str(update_data.website) if update_data.website else None
        normalized_updates["normalized_website"] = normalize_website_for_comparison(
            str(update_data.website) if update_data.website else None
        )
    
    if update_data.industry is not None:
        update_doc["industry"] = update_data.industry
    
    if update_data.description is not None:
        update_doc["description"] = update_data.description
    
    if update_data.headquarters_country is not None:
        update_doc["headquarters_country"] = update_data.headquarters_country
    
    if update_data.headquarters_region is not None:
        update_doc["headquarters_region"] = update_data.headquarters_region
    
    if update_data.employee_count is not None:
        update_doc["employee_count"] = update_data.employee_count
    
    if not update_doc:
        # No fields to update, just return current record
        return get_company(company_id)
    
    # Add normalized fields and timestamp
    update_doc.update(normalized_updates)
    update_doc["updated_at"] = datetime.now(timezone.utc)
    
    try:
        result = collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_doc},
            return_document=True
        )
        
        if result is None:
            raise CompanyNotFoundError(f"Company with ID {company_id} not found")
        
        return document_to_response(result)
    except DuplicateKeyError as e:
        # Determine which field caused the duplicate
        if "normalized_name" in str(e):
            raise DuplicateCompanyError(
                f"Company with name '{update_data.company_name}' already exists",
                "company_name"
            )
        elif "normalized_website" in str(e):
            raise DuplicateCompanyError(
                f"Company with website '{update_data.website}' already exists",
                "website"
            )
        else:
            raise DuplicateCompanyError("Duplicate company detected", "unknown")


def delete_company(company_id: str) -> None:
    """
    Delete a company record.
    
    Args:
        company_id: Company ID
        
    Raises:
        CompanyNotFoundError: If company does not exist
        ValueError: If company_id is not a valid ObjectId
        DatabaseConnectionError: If database is not available
    """
    collection = get_companies_collection()
    
    try:
        object_id = ObjectId(company_id)
    except Exception:
        raise ValueError(f"Invalid company ID format: {company_id}")
    
    result = collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise CompanyNotFoundError(f"Company with ID {company_id} not found")
