"""Research data access layer."""
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.db.mongodb import mongodb
from app.db.companies import DatabaseConnectionError
from app.models.research import (
    ResearchRunResponse,
    SourceEvidenceResponse,
    ResearchStatus
)


class ResearchNotFoundError(Exception):
    """Raised when a research run is not found."""
    pass


class SourceNotFoundError(Exception):
    """Raised when a source is not found."""
    pass


def get_research_runs_collection():
    """Get the research_runs collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.research_runs


def get_source_evidence_collection():
    """Get the source_evidence collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.source_evidence


def ensure_research_indexes():
    """
    Create necessary indexes for research collections.
    
    Creates indexes for:
    - research_runs: company_id, status, started_at
    - source_evidence: research_run_id, company_id, source_url
    """
    try:
        # Research runs indexes
        runs_collection = get_research_runs_collection()
        
        runs_collection.create_index(
            [("company_id", 1), ("started_at", -1)],
            name="company_started_desc"
        )
        
        runs_collection.create_index(
            [("status", 1)],
            name="status_idx"
        )
        
        # Source evidence indexes
        sources_collection = get_source_evidence_collection()
        
        sources_collection.create_index(
            [("research_run_id", 1), ("retrieved_at", -1)],
            name="run_retrieved_desc"
        )
        
        sources_collection.create_index(
            [("company_id", 1), ("retrieved_at", -1)],
            name="company_retrieved_desc"
        )
        
        # Index for deduplication within a research run
        sources_collection.create_index(
            [("research_run_id", 1), ("normalized_url", 1)],
            name="run_normalized_url"
        )
        
    except PyMongoError:
        # If index creation fails, log but don't crash
        pass


def normalize_url(url: str) -> str:
    """
    Normalize URL for deduplication.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL string
    """
    # Parse and normalize URL
    parsed = urlparse(url.lower().strip())
    
    # Remove trailing slash from path
    path = parsed.path.rstrip('/') if parsed.path else ''
    
    # Reconstruct normalized URL
    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"
    
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain name
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc or url
    except Exception:
        return url


def research_run_to_response(doc: dict) -> ResearchRunResponse:
    """
    Convert MongoDB document to ResearchRunResponse.
    
    Args:
        doc: MongoDB document
        
    Returns:
        ResearchRunResponse model
    """
    return ResearchRunResponse(
        id=str(doc["_id"]),
        company_id=str(doc["company_id"]),
        status=doc["status"],
        started_at=doc["started_at"],
        completed_at=doc.get("completed_at"),
        queries_executed=doc.get("queries_executed", 0),
        sources_found=doc.get("sources_found", 0),
        sources_saved=doc.get("sources_saved", 0),
        error_summary=doc.get("error_summary")
    )


def source_evidence_to_response(doc: dict) -> SourceEvidenceResponse:
    """
    Convert MongoDB document to SourceEvidenceResponse.
    
    Args:
        doc: MongoDB document
        
    Returns:
        SourceEvidenceResponse model
    """
    return SourceEvidenceResponse(
        id=str(doc["_id"]),
        research_run_id=str(doc["research_run_id"]),
        company_id=str(doc["company_id"]),
        source_url=doc["source_url"],
        source_domain=doc["source_domain"],
        title=doc["title"],
        snippet=doc["snippet"],
        published_at=doc.get("published_at"),
        retrieved_at=doc["retrieved_at"],
        provider=doc["provider"],
        content_type=doc.get("content_type")
    )


def create_research_run(company_id: str) -> ResearchRunResponse:
    """
    Create a new research run record.
    
    Args:
        company_id: Company ID (as string)
        
    Returns:
        Created research run
        
    Raises:
        DatabaseConnectionError: If database is not available
    """
    collection = get_research_runs_collection()
    
    # Convert company_id string to ObjectId for consistency
    company_object_id = ObjectId(company_id)
    
    doc = {
        "company_id": company_object_id,
        "status": "pending",
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
        "queries_executed": 0,
        "sources_found": 0,
        "sources_saved": 0,
        "error_summary": None
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    return research_run_to_response(doc)


def update_research_run(
    research_run_id: str,
    status: Optional[ResearchStatus] = None,
    queries_executed: Optional[int] = None,
    sources_found: Optional[int] = None,
    sources_saved: Optional[int] = None,
    error_summary: Optional[str] = None
) -> ResearchRunResponse:
    """
    Update a research run record.
    
    Args:
        research_run_id: Research run ID
        status: New status
        queries_executed: Number of queries executed
        sources_found: Number of sources found
        sources_saved: Number of sources saved
        error_summary: Error summary
        
    Returns:
        Updated research run
        
    Raises:
        ResearchNotFoundError: If research run does not exist
        ValueError: If research_run_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_research_runs_collection()
    
    try:
        object_id = ObjectId(research_run_id)
    except Exception:
        raise ValueError(f"Invalid research run ID format: {research_run_id}")
    
    update_doc = {}
    
    if status is not None:
        update_doc["status"] = status
        # Set completed_at when status changes to completed, partial, or failed
        if status in ["completed", "partial", "failed"]:
            update_doc["completed_at"] = datetime.now(timezone.utc)
    
    if queries_executed is not None:
        update_doc["queries_executed"] = queries_executed
    
    if sources_found is not None:
        update_doc["sources_found"] = sources_found
    
    if sources_saved is not None:
        update_doc["sources_saved"] = sources_saved
    
    if error_summary is not None:
        update_doc["error_summary"] = error_summary
    
    if not update_doc:
        # Nothing to update
        return get_research_run(research_run_id)
    
    result = collection.find_one_and_update(
        {"_id": object_id},
        {"$set": update_doc},
        return_document=True
    )
    
    if result is None:
        raise ResearchNotFoundError(f"Research run with ID {research_run_id} not found")
    
    return research_run_to_response(result)


def get_research_run(research_run_id: str, company_id: Optional[str] = None) -> ResearchRunResponse:
    """
    Get a research run by ID.
    
    Args:
        research_run_id: Research run ID
        company_id: Optional company ID to validate ownership
        
    Returns:
        Research run record
        
    Raises:
        ResearchNotFoundError: If research run does not exist or doesn't belong to company
        ValueError: If IDs are invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_research_runs_collection()
    
    try:
        object_id = ObjectId(research_run_id)
    except Exception:
        raise ValueError(f"Invalid research run ID format: {research_run_id}")
    
    query = {"_id": object_id}
    
    if company_id:
        try:
            query["company_id"] = ObjectId(company_id)
        except Exception:
            raise ValueError(f"Invalid company ID format: {company_id}")
    
    doc = collection.find_one(query)
    
    if doc is None:
        if company_id:
            raise ResearchNotFoundError(
                f"Research run with ID {research_run_id} not found for company {company_id}"
            )
        raise ResearchNotFoundError(f"Research run with ID {research_run_id} not found")
    
    return research_run_to_response(doc)


def list_research_runs(
    company_id: str,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[ResearchRunResponse], int]:
    """
    List research runs for a company.
    
    Args:
        company_id: Company ID
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of research runs, total count)
        
    Raises:
        ValueError: If company_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_research_runs_collection()
    
    try:
        company_object_id = ObjectId(company_id)
    except Exception:
        raise ValueError(f"Invalid company ID format: {company_id}")
    
    query = {"company_id": company_object_id}
    
    # Get total count
    total = collection.count_documents(query)
    
    # Get paginated results, sorted by started_at descending (newest first)
    cursor = collection.find(query).sort("started_at", -1).skip(offset).limit(limit)
    
    runs = [research_run_to_response(doc) for doc in cursor]
    
    return runs, total


def save_source_evidence(
    research_run_id: str,
    company_id: str,
    source_url: str,
    title: str,
    snippet: str,
    published_at: Optional[datetime] = None,
    content_type: Optional[str] = None
) -> Optional[SourceEvidenceResponse]:
    """
    Save source evidence from a search result.
    
    Args:
        research_run_id: Research run ID
        company_id: Company ID
        source_url: Source URL
        title: Source title
        snippet: Content snippet (will be truncated if too long)
        published_at: Publication date (optional)
        content_type: Content type or category (optional)
        
    Returns:
        Saved source evidence, or None if duplicate within same run
        
    Raises:
        ValueError: If IDs are invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_source_evidence_collection()
    
    try:
        run_object_id = ObjectId(research_run_id)
        company_object_id = ObjectId(company_id)
    except Exception as e:
        raise ValueError(f"Invalid ID format: {e}")
    
    # Normalize URL for deduplication
    normalized_url = normalize_url(source_url)
    
    # Check if this source already exists in this research run
    existing = collection.find_one({
        "research_run_id": run_object_id,
        "normalized_url": normalized_url
    })
    
    if existing:
        # Skip duplicate within same run
        return None
    
    # Extract domain
    domain = extract_domain(source_url)
    
    # Truncate snippet if too long (keep reasonable storage size)
    max_snippet_length = 1000
    if len(snippet) > max_snippet_length:
        snippet = snippet[:max_snippet_length] + "..."
    
    doc = {
        "research_run_id": run_object_id,
        "company_id": company_object_id,
        "source_url": source_url,
        "normalized_url": normalized_url,
        "source_domain": domain,
        "title": title,
        "snippet": snippet,
        "published_at": published_at,
        "retrieved_at": datetime.now(timezone.utc),
        "provider": "Tavily",
        "content_type": content_type
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    return source_evidence_to_response(doc)


def list_source_evidence(
    research_run_id: str,
    company_id: str,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[SourceEvidenceResponse], int]:
    """
    List source evidence for a research run.
    
    Args:
        research_run_id: Research run ID
        company_id: Company ID (for validation)
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of sources, total count)
        
    Raises:
        ValueError: If IDs are invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_source_evidence_collection()
    
    try:
        run_object_id = ObjectId(research_run_id)
        company_object_id = ObjectId(company_id)
    except Exception:
        raise ValueError("Invalid ID format")
    
    query = {
        "research_run_id": run_object_id,
        "company_id": company_object_id
    }
    
    # Get total count
    total = collection.count_documents(query)
    
    # Get paginated results, sorted by retrieved_at descending
    cursor = collection.find(query).sort("retrieved_at", -1).skip(offset).limit(limit)
    
    sources = [source_evidence_to_response(doc) for doc in cursor]
    
    return sources, total
