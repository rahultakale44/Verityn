"""Qualification data access layer."""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.db.mongodb import mongodb
from app.db.companies import DatabaseConnectionError
from app.models.qualification import (
    QualificationResponse,
    CriterionEvaluation,
    QualificationOutcome
)


class QualificationNotFoundError(Exception):
    """Raised when a qualification is not found."""
    pass


def get_qualifications_collection():
    """Get the qualifications collection."""
    db = mongodb.get_database()
    if db is None:
        raise DatabaseConnectionError("Database connection not available")
    return db.qualifications


def ensure_qualification_indexes():
    """
    Create necessary indexes for the qualifications collection.
    
    Creates indexes for:
    - company_id and qualified_at for listing
    - icp_id for filtering
    - outcome for filtering
    """
    try:
        collection = get_qualifications_collection()
        
        collection.create_index(
            [("company_id", 1), ("qualified_at", -1)],
            name="company_qualified_desc"
        )
        
        collection.create_index(
            [("icp_id", 1)],
            name="icp_idx"
        )
        
        collection.create_index(
            [("outcome", 1)],
            name="outcome_idx"
        )
        
    except PyMongoError:
        pass


def criterion_evaluation_to_dict(evaluation: CriterionEvaluation) -> dict:
    """Convert CriterionEvaluation to dict for storage."""
    return {
        "criterion_id": evaluation.criterion_id,
        "criterion_name": evaluation.criterion_name,
        "weight": evaluation.weight,
        "status": evaluation.status,
        "explanation": evaluation.explanation,
        "observed_value": evaluation.observed_value,
        "expected_value": evaluation.expected_value,
        "evidence_references": [
            {
                "source_id": ref.source_id,
                "source_url": ref.source_url,
                "title": ref.title,
                "snippet": ref.snippet
            }
            for ref in evaluation.evidence_references
        ],
        "reason_insufficient": evaluation.reason_insufficient
    }


def dict_to_criterion_evaluation(data: dict) -> CriterionEvaluation:
    """Convert dict to CriterionEvaluation."""
    from app.models.qualification import EvidenceReference
    
    return CriterionEvaluation(
        criterion_id=data["criterion_id"],
        criterion_name=data["criterion_name"],
        weight=data["weight"],
        status=data["status"],
        explanation=data["explanation"],
        observed_value=data.get("observed_value"),
        expected_value=data.get("expected_value"),
        evidence_references=[
            EvidenceReference(**ref) for ref in data.get("evidence_references", [])
        ],
        reason_insufficient=data.get("reason_insufficient")
    )


def document_to_response(doc: dict) -> QualificationResponse:
    """
    Convert MongoDB document to QualificationResponse.
    
    Args:
        doc: MongoDB document
        
    Returns:
        QualificationResponse model
    """
    return QualificationResponse(
        id=str(doc["_id"]),
        company_id=str(doc["company_id"]),
        icp_id=str(doc["icp_id"]),
        icp_snapshot=doc["icp_snapshot"],
        qualified_at=doc["qualified_at"],
        score=doc.get("score"),
        evidence_coverage=doc.get("evidence_coverage"),
        outcome=doc["outcome"],
        outcome_explanation=doc["outcome_explanation"],
        criteria_evaluations=[
            dict_to_criterion_evaluation(e) for e in doc["criteria_evaluations"]
        ],
        limitations=doc.get("limitations")
    )


def create_qualification(
    company_id: str,
    icp_id: str,
    icp_snapshot: Dict[str, Any],
    score: Optional[float],
    evidence_coverage: Optional[float],
    outcome: QualificationOutcome,
    outcome_explanation: str,
    criteria_evaluations: list[CriterionEvaluation],
    limitations: Optional[str]
) -> QualificationResponse:
    """
    Create a new qualification result.
    
    Args:
        company_id: Company ID
        icp_id: ICP ID
        icp_snapshot: Immutable snapshot of ICP configuration
        score: Qualification score (0-100 or None)
        evidence_coverage: Evidence coverage percentage (0-100 or None)
        outcome: Qualification outcome
        outcome_explanation: Explanation of outcome
        criteria_evaluations: List of criterion evaluations
        limitations: Known limitations
        
    Returns:
        Created qualification result
        
    Raises:
        ValueError: If IDs are invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_qualifications_collection()
    
    try:
        company_object_id = ObjectId(company_id)
        icp_object_id = ObjectId(icp_id)
    except Exception as e:
        raise ValueError(f"Invalid ID format: {e}")
    
    doc = {
        "company_id": company_object_id,
        "icp_id": icp_object_id,
        "icp_snapshot": icp_snapshot,
        "qualified_at": datetime.now(timezone.utc),
        "score": score,
        "evidence_coverage": evidence_coverage,
        "outcome": outcome,
        "outcome_explanation": outcome_explanation,
        "criteria_evaluations": [
            criterion_evaluation_to_dict(e) for e in criteria_evaluations
        ],
        "limitations": limitations
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    
    return document_to_response(doc)


def get_qualification(
    qualification_id: str,
    company_id: Optional[str] = None
) -> QualificationResponse:
    """
    Get a qualification by ID.
    
    Args:
        qualification_id: Qualification ID
        company_id: Optional company ID to validate ownership
        
    Returns:
        Qualification record
        
    Raises:
        QualificationNotFoundError: If qualification does not exist or doesn't belong to company
        ValueError: If IDs are invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_qualifications_collection()
    
    try:
        object_id = ObjectId(qualification_id)
    except Exception:
        raise ValueError(f"Invalid qualification ID format: {qualification_id}")
    
    query = {"_id": object_id}
    
    if company_id:
        try:
            query["company_id"] = ObjectId(company_id)
        except Exception:
            raise ValueError(f"Invalid company ID format: {company_id}")
    
    doc = collection.find_one(query)
    
    if doc is None:
        if company_id:
            raise QualificationNotFoundError(
                f"Qualification with ID {qualification_id} not found for company {company_id}"
            )
        raise QualificationNotFoundError(f"Qualification with ID {qualification_id} not found")
    
    return document_to_response(doc)


def list_qualifications(
    company_id: str,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[QualificationResponse], int]:
    """
    List qualification results for a company.
    
    Args:
        company_id: Company ID
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (list of qualifications, total count)
        
    Raises:
        ValueError: If company_id is invalid
        DatabaseConnectionError: If database is not available
    """
    collection = get_qualifications_collection()
    
    try:
        company_object_id = ObjectId(company_id)
    except Exception:
        raise ValueError(f"Invalid company ID format: {company_id}")
    
    query = {"company_id": company_object_id}
    
    # Get total count
    total = collection.count_documents(query)
    
    # Get paginated results, sorted by qualified_at descending (newest first)
    cursor = collection.find(query).sort("qualified_at", -1).skip(offset).limit(limit)
    
    qualifications = [document_to_response(doc) for doc in cursor]
    
    return qualifications, total
