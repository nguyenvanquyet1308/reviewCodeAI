from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class ReviewIssue(BaseModel):
    file: str
    line: str
    level: str  # LOW | MEDIUM | HIGH
    issue: str
    suggestion: str

class SuggestedTestCase(BaseModel):
    name: str
    description: str
    priority: str  # LOW | MEDIUM | HIGH

class MergeRecommendation(BaseModel):
    can_merge: bool
    reason: str

class ReviewResultDTO(BaseModel):
    summary: str
    potential_bugs: List[ReviewIssue] = Field(default_factory=list)
    security_issues: List[ReviewIssue] = Field(default_factory=list)
    code_smells: List[ReviewIssue] = Field(default_factory=list)
    performance_issues: List[ReviewIssue] = Field(default_factory=list)
    suggested_test_cases: List[SuggestedTestCase] = Field(default_factory=list)
    risk_level: str  # LOW | MEDIUM | HIGH
    merge_recommendation: MergeRecommendation

class ReviewResultResponse(BaseModel):
    id: int
    review_job_id: int
    summary: str
    potential_bugs: List[Dict[str, Any]]
    security_issues: List[Dict[str, Any]]
    code_smells: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    suggested_test_cases: List[Dict[str, Any]]
    risk_level: str
    merge_recommendation: Dict[str, Any]
    ai_raw_response: str
    github_comment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewDetailResponse(BaseModel):
    id: int
    review_job_id: int
    repository_name: str
    pr_number: int
    pr_title: str
    pr_author: str
    pr_url: str
    status: str
    summary: str
    potential_bugs: List[Dict[str, Any]]
    security_issues: List[Dict[str, Any]]
    code_smells: List[Dict[str, Any]]
    performance_issues: List[Dict[str, Any]]
    suggested_test_cases: List[Dict[str, Any]]
    risk_level: str
    merge_recommendation: Dict[str, Any]
    ai_raw_response: str
    github_comment_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
