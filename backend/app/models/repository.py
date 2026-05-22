from datetime import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, BigInteger, String, DateTime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.db.session import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(BigInteger, unique=True, index=True, nullable=False)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
