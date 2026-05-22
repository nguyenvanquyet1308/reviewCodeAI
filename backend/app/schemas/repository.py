from datetime import datetime
from pydantic import BaseModel, ConfigDict

class RepositoryBase(BaseModel):
    github_repo_id: int
    owner: str
    name: str
    full_name: str
    html_url: str

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
