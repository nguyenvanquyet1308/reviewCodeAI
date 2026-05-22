from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.db.session import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    github_pr_id = Column(BigInteger, nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    source_branch = Column(String, nullable=False)
    target_branch = Column(String, nullable=False)
    state = Column(String, nullable=False)
    html_url = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    repository = relationship("Repository", back_populates="pull_requests")
    review_jobs = relationship("ReviewJob", back_populates="pull_request", cascade="all, delete-orphan")
