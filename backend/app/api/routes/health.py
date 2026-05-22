from fastapi import APIRouter

router = APIRouter()

@router.get("", status_code=200)
def health_check():
    """
    Simple health check API to verify backend availability.
    """
    return {
        "status": "ok",
        "service": "AI GitHub Code Review Platform"
    }
