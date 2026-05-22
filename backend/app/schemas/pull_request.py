from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PullRequestBase(BaseModel):
    github_pr_id: int
    pr_number: int
    title: str
    author: str
    source_branch: str
    target_branch: str
    state: str
    html_url: str

class PullRequestCreate(PullRequestBase):
    repository_id: int

class PullRequestResponse(PullRequestBase):
    id: int
    repository_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
