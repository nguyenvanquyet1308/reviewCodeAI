from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.db.session import Base

class ReviewJob(Base):
    __tablename__ = "review_jobs"

    id = Column(Integer, primary_key=True, index=True)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, running, success, failed
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    pull_request = relationship("PullRequest", back_populates="review_jobs")
    review_results = relationship("ReviewResult", back_populates="review_job", cascade="all, delete-orphan")
