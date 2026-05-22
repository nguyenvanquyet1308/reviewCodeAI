from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    """
    Test that the health endpoint returns 200 and correct status message.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "AI GitHub Code Review Platform"
    }
