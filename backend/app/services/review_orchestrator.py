import logging
from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from app.models.review_job import ReviewJob
from app.models.review_result import ReviewResult
from app.services.github_service import GitHubService
from app.services.ai_review_service import AIReviewService
from app.services.comment_formatter import CommentFormatter

logger = logging.getLogger("ai_review_platform")

class ReviewOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.github_service = GitHubService()
        self.ai_service = AIReviewService()

    def orchestrate_review(self, review_job_id: int) -> None:
        """
        Execute the complete review pipeline:
        1. Fetch job from DB and set status to 'running'
        2. Download code differences from GitHub
        3. Feed differences to OpenAI
        4. Comment structured findings back to PR
        5. Log final results and set status to 'success'
        """
        job = self.db.query(ReviewJob).filter(ReviewJob.id == review_job_id).first()
        if not job:
            logger.error(f"Review job with ID {review_job_id} not found.")
            return

        logger.info(f"Starting review orchestration for job {review_job_id}")
        job.status = "running"
        job.started_at = datetime.utcnow()
        self.db.commit()

        try:
            pr = job.pull_request
            repo = pr.repository
            
            # Step 1: Get Diff from GitHub
            logger.info(f"Fetching diff for PR #{pr.pr_number} in {repo.full_name}")
            diff_text = self.github_service.get_pull_request_diff(
                owner=repo.owner,
                repo=repo.name,
                pr_number=pr.pr_number
            )
            
            # Step 2: Get AI Review
            logger.info("Running AI Review on diff...")
            review_dto = self.ai_service.review_pull_request(
                diff_text=diff_text,
                repository_name=repo.full_name,
                pr_title=pr.title
            )
            
            # Step 3: Format PR comment
            logger.info("Formatting PR comment...")
            comment_markdown = CommentFormatter.format_comment(review_dto)
            
            # Step 4: Post comment to GitHub
            logger.info("Posting review comment to GitHub...")
            comment_url = None
            try:
                comment_url = self.github_service.create_pr_comment(
                    owner=repo.owner,
                    repo=repo.name,
                    pr_number=pr.pr_number,
                    body=comment_markdown
                )
            except Exception as e:
                logger.error(f"Failed to post comment to GitHub: {str(e)}")
                # We do not fail the whole transaction if commenting fails; we still save the DB record.

            # Step 5: Save Review Result to DB
            logger.info("Saving review result to database...")
            # Convert DTO Pydantic lists to list of dicts for JSON storage
            bugs_dict = [bug.model_dump() for bug in review_dto.potential_bugs]
            security_dict = [sec.model_dump() for sec in review_dto.security_issues]
            smells_dict = [smell.model_dump() for smell in review_dto.code_smells]
            perf_dict = [perf.model_dump() for perf in review_dto.performance_issues]
            tests_dict = [tc.model_dump() for tc in review_dto.suggested_test_cases]
            rec_dict = review_dto.merge_recommendation.model_dump()
            
            raw_response = review_dto.model_dump_json(indent=2)

            result = ReviewResult(
                review_job_id=job.id,
                summary=review_dto.summary,
                potential_bugs=bugs_dict,
                security_issues=security_dict,
                code_smells=smells_dict,
                performance_issues=perf_dict,
                suggested_test_cases=tests_dict,
                risk_level=review_dto.risk_level,
                merge_recommendation=rec_dict,
                ai_raw_response=raw_response,
                github_comment_url=comment_url
            )
            self.db.add(result)
            
            job.status = "success"
            logger.info(f"Review job {review_job_id} completed successfully.")

        except Exception as e:
            logger.exception(f"Error during review orchestration for job {review_job_id}")
            job.status = "failed"
            job.error_message = str(e)
            
        finally:
            job.completed_at = datetime.utcnow()
            self.db.commit()
