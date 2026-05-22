import logging
from fastapi import APIRouter, Request, Header, HTTPException, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.services.github_service import GitHubService
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review_job import ReviewJob
from app.workers.review_tasks import process_review_job

logger = logging.getLogger("ai_review_platform")
router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive webhook event from GitHub.
    Verifies signature, filters for pull_request events,
    records repo/PR details, and queues an AI review task.
    """
    # Read raw body to verify signature
    body = await request.body()
    
    # 1. Verify signature
    github_service = GitHubService()
    if not github_service.verify_webhook_signature(body, x_hub_signature_256):
        logger.warning("Webhook signature verification failed.")
        raise HTTPException(status_code=401, detail="Signature verification failed")

    # 2. Only process pull_request events
    if x_github_event != "pull_request":
        logger.info(f"Skipping non-pull_request event: {x_github_event}")
        return {"message": f"Skipped event: {x_github_event}"}

    # Parse JSON body
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    action = payload.get("action")
    pr_data = payload.get("pull_request")
    repo_data = payload.get("repository")

    if not pr_data or not repo_data:
        raise HTTPException(status_code=400, detail="Missing pull_request or repository in payload")

    # 3. Only process specific actions
    allowed_actions = ["opened", "synchronize", "reopened", "ready_for_review"]
    if action not in allowed_actions:
        logger.info(f"Skipping action: {action}")
        return {"message": f"Skipped action: {action}"}

    # 4. Skip draft PRs if configured
    is_draft = pr_data.get("draft", False)
    if is_draft and not settings.REVIEW_DRAFT_PR:
        logger.info("Skipping draft Pull Request as configured.")
        return {"message": "Skipped draft Pull Request"}

    # 5. Upsert Repository record
    github_repo_id = repo_data.get("id")
    owner = repo_data.get("owner", {}).get("login")
    repo_name = repo_data.get("name")
    full_name = repo_data.get("full_name")
    repo_url = repo_data.get("html_url")

    repo_record = db.query(Repository).filter(Repository.github_repo_id == github_repo_id).first()
    if not repo_record:
        repo_record = Repository(
            github_repo_id=github_repo_id,
            owner=owner,
            name=repo_name,
            full_name=full_name,
            html_url=repo_url
        )
        db.add(repo_record)
        db.flush()
    else:
        repo_record.owner = owner
        repo_record.name = repo_name
        repo_record.full_name = full_name
        repo_record.html_url = repo_url
        db.flush()

    # 6. Upsert Pull Request record
    github_pr_id = pr_data.get("id")
    pr_number = pr_data.get("number")
    pr_title = pr_data.get("title")
    pr_author = pr_data.get("user", {}).get("login")
    source_branch = pr_data.get("head", {}).get("ref")
    target_branch = pr_data.get("base", {}).get("ref")
    pr_state = pr_data.get("state")
    pr_url = pr_data.get("html_url")

    pr_record = db.query(PullRequest).filter(
        PullRequest.repository_id == repo_record.id,
        PullRequest.github_pr_id == github_pr_id
    ).first()

    if not pr_record:
        pr_record = PullRequest(
            repository_id=repo_record.id,
            github_pr_id=github_pr_id,
            pr_number=pr_number,
            title=pr_title,
            author=pr_author,
            source_branch=source_branch,
            target_branch=target_branch,
            state=pr_state,
            html_url=pr_url
        )
        db.add(pr_record)
        db.flush()
    else:
        pr_record.title = pr_title
        pr_record.state = pr_state
        pr_record.source_branch = source_branch
        pr_record.target_branch = target_branch
        db.flush()

    # 7. Create Review Job
    job = ReviewJob(
        pull_request_id=pr_record.id,
        status="pending"
    )
    db.add(job)
    db.commit()

    # 8. Queue Celery Task
    logger.info(f"Enqueuing review job ID {job.id} for PR #{pr_number}")
    process_review_job.delay(job.id)

    return {
        "status": "queued",
        "job_id": job.id,
        "repository": repo_record.full_name,
        "pr_number": pr_number
    }
