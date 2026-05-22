import logging
import httpx
from typing import List, Dict, Any
from app.core.config import settings
from app.core.security import verify_github_signature
from app.core.exceptions import GitHubAPIException

logger = logging.getLogger("ai_review_platform")

class GitHubService:
    def __init__(self, token: str = None, webhook_secret: str = None):
        self.token = token or settings.GITHUB_TOKEN
        self.webhook_secret = webhook_secret or settings.GITHUB_WEBHOOK_SECRET
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def verify_webhook_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """
        Verify the signature of an incoming GitHub webhook.
        """
        if not self.webhook_secret:
            logger.warning("GITHUB_WEBHOOK_SECRET is not configured, signature verification skipped.")
            return True
        return verify_github_signature(payload_body, signature_header, self.webhook_secret)

    def get_pull_request_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Fetch the Pull Request diff from GitHub.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    raise GitHubAPIException(f"Failed to fetch PR diff: {response.text}", response.status_code)
                return response.text
        except httpx.RequestError as e:
            raise GitHubAPIException(f"Request error occurred while fetching PR diff: {str(e)}")

    def create_pr_comment(self, owner: str, repo: str, pr_number: int, body: str) -> str:
        """
        Post a comment to the Pull Request.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        payload = {"body": body}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=self.headers, json=payload)
                if response.status_code != 201:
                    raise GitHubAPIException(f"Failed to create PR comment: {response.text}", response.status_code)
                comment_data = response.json()
                return comment_data.get("html_url", "")
        except httpx.RequestError as e:
            raise GitHubAPIException(f"Request error occurred while creating comment: {str(e)}")

    def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Retrieve list of files modified in the Pull Request.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                if response.status_code != 200:
                    raise GitHubAPIException(f"Failed to fetch PR files: {response.text}", response.status_code)
                return response.json()
        except httpx.RequestError as e:
            raise GitHubAPIException(f"Request error occurred while fetching PR files: {str(e)}")
