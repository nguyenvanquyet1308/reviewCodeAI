from fastapi import HTTPException, status

class PlatformException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class GitHubAPIException(PlatformException):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(f"GitHub API Error: {message}", status_code)

class AIReviewException(PlatformException):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(f"AI Review Error: {message}", status_code)
