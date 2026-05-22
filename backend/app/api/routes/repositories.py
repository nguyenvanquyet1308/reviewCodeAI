from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
# pyrefly: ignore [missing-import]
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db.session import get_db
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review_job import ReviewJob

router = APIRouter()

class RepositoryListResponse(BaseModel):
    id: int
    full_name: str
    html_url: str
    review_count: int
    last_reviewed_at: Optional[datetime] = None

@router.get("", response_model=List[RepositoryListResponse])
def list_repositories(db: Session = Depends(get_db)):
    """
    Retrieve all repositories registered via webhooks,
    aggregating total review count and last review completion timestamp.
    """
    query = db.query(
        Repository.id,
        Repository.full_name,
        Repository.html_url,
        func.count(ReviewJob.id).label("review_count"),
        func.max(ReviewJob.completed_at).label("last_reviewed_at")
    ).outerjoin(
        PullRequest, PullRequest.repository_id == Repository.id
    ).outerjoin(
        ReviewJob, ReviewJob.pull_request_id == PullRequest.id
    ).group_by(
        Repository.id, Repository.full_name, Repository.html_url
    ).order_by(
        Repository.full_name
    )
    
    results = query.all()
    
    formatted_results = []
    for r in results:
        formatted_results.append({
            "id": r.id,
            "full_name": r.full_name,
            "html_url": r.html_url,
            "review_count": r.review_count,
            "last_reviewed_at": r.last_reviewed_at
        })
    return formatted_results
