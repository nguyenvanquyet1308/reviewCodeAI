import logging
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.review_orchestrator import ReviewOrchestrator

logger = logging.getLogger("ai_review_platform")

@celery_app.task(name="app.workers.review_tasks.process_review_job")
def process_review_job(review_job_id: int) -> None:
    """
    Celery worker task to process an AI Code Review Job.
    """
    logger.info(f"Celery task received for job ID: {review_job_id}")
    db = SessionLocal()
    try:
        orchestrator = ReviewOrchestrator(db=db)
        orchestrator.orchestrate_review(review_job_id=review_job_id)
    except Exception as e:
        logger.exception(f"Unhandled exception in Celery task for job {review_job_id}: {str(e)}")
    finally:
        db.close()
        logger.info(f"Database session closed for job {review_job_id}")
