from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ReviewJobBase(BaseModel):
    pull_request_id: int
    status: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ReviewJobCreate(BaseModel):
    pull_request_id: int

class ReviewJobResponse(ReviewJobBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewJobListResponse(BaseModel):
    id: int
    repository_name: str
    pr_number: int
    pr_title: str
    author: str
    status: str
    risk_level: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
