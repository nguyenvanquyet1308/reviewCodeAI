from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.db.session import Base

class ReviewResult(Base):
    __tablename__ = "review_results"

    id = Column(Integer, primary_key=True, index=True)
    review_job_id = Column(Integer, ForeignKey("review_jobs.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    potential_bugs = Column(JSON, default=list, nullable=False)
    security_issues = Column(JSON, default=list, nullable=False)
    code_smells = Column(JSON, default=list, nullable=False)
    performance_issues = Column(JSON, default=list, nullable=False)
    suggested_test_cases = Column(JSON, default=list, nullable=False)
    risk_level = Column(String, default="LOW", nullable=False)  # LOW, MEDIUM, HIGH
    merge_recommendation = Column(JSON, default=dict, nullable=False)
    ai_raw_response = Column(Text, nullable=False)
    github_comment_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    review_job = relationship("ReviewJob", back_populates="review_results")
