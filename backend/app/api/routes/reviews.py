from fastapi import APIRouter, Depends, HTTPException, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.review_job import ReviewJob
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_result import ReviewResult
from app.schemas.review_job import ReviewJobListResponse
from app.schemas.review_result import ReviewDetailResponse

router = APIRouter()

@router.get("", response_model=List[ReviewJobListResponse])
def list_reviews(
    repository: Optional[str] = Query(None, description="Filter by repository name"),
    status: Optional[str] = Query(None, description="Filter by review status"),
    risk_level: Optional[str] = Query(None, description="Filter by AI risk level"),
    db: Session = Depends(get_db)
):
    """
    List and filter all AI code review jobs.
    """
    query = db.query(
        ReviewJob.id,
        Repository.full_name.label("repository_name"),
        PullRequest.pr_number,
        PullRequest.title.label("pr_title"),
        PullRequest.author,
        ReviewJob.status,
        ReviewResult.risk_level,
        ReviewJob.created_at,
        ReviewJob.completed_at
    ).join(
        PullRequest, ReviewJob.pull_request_id == PullRequest.id
    ).join(
        Repository, PullRequest.repository_id == Repository.id
    ).outerjoin(
        ReviewResult, ReviewResult.review_job_id == ReviewJob.id
    )

    if repository:
        query = query.filter(Repository.full_name.ilike(f"%{repository}%"))
    if status:
        query = query.filter(ReviewJob.status == status)
    if risk_level:
        query = query.filter(ReviewResult.risk_level == risk_level)

    query = query.order_by(ReviewJob.created_at.desc())
    results = query.all()
    
    # Format database rows into dictionaries matching ReviewJobListResponse fields
    formatted_results = []
    for r in results:
        formatted_results.append({
            "id": r.id,
            "repository_name": r.repository_name,
            "pr_number": r.pr_number,
            "pr_title": r.pr_title,
            "author": r.author,
            "status": r.status,
            "risk_level": r.risk_level,
            "created_at": r.created_at,
            "completed_at": r.completed_at
        })
    return formatted_results

@router.get("/{review_id}", response_model=ReviewDetailResponse)
def get_review_detail(review_id: int, db: Session = Depends(get_db)):
    """
    Get detailed AI analysis results for a specific review job.
    """
    job = db.query(ReviewJob).filter(ReviewJob.id == review_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Review job not found")
        
    pr = job.pull_request
    repo = pr.repository
    result = db.query(ReviewResult).filter(ReviewResult.review_job_id == review_id).first()
    
    summary = ""
    potential_bugs = []
    security_issues = []
    code_smells = []
    performance_issues = []
    suggested_test_cases = []
    risk_level = "LOW"
    merge_recommendation = {"can_merge": True, "reason": "Job is pending or failed."}
    ai_raw_response = ""
    github_comment_url = None
    
    if result:
        summary = result.summary
        potential_bugs = result.potential_bugs
        security_issues = result.security_issues
        code_smells = result.code_smells
        performance_issues = result.performance_issues
        suggested_test_cases = result.suggested_test_cases
        risk_level = result.risk_level
        merge_recommendation = result.merge_recommendation
        ai_raw_response = result.ai_raw_response
        github_comment_url = result.github_comment_url
    elif job.status == "failed":
        summary = f"Review job failed. Error: {job.error_message}"
        merge_recommendation = {"can_merge": False, "reason": f"Execution failed: {job.error_message}"}
    elif job.status == "running" or job.status == "pending":
        summary = "AI Review is currently in progress..."
        merge_recommendation = {"can_merge": False, "reason": "Review is still processing."}

    return ReviewDetailResponse(
        id=job.id,
        review_job_id=job.id,
        repository_name=repo.full_name,
        pr_number=pr.pr_number,
        pr_title=pr.title,
        pr_author=pr.author,
        pr_url=pr.html_url,
        status=job.status,
        summary=summary,
        potential_bugs=potential_bugs,
        security_issues=security_issues,
        code_smells=code_smells,
        performance_issues=performance_issues,
        suggested_test_cases=suggested_test_cases,
        risk_level=risk_level,
        merge_recommendation=merge_recommendation,
        ai_raw_response=ai_raw_response,
        github_comment_url=github_comment_url,
        created_at=job.created_at
    )
