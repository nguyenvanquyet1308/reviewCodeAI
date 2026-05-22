import json
from app.schemas.review_result import ReviewResultDTO

def test_parse_ai_response_valid():
    """
    Test that a valid JSON structure maps correctly to the ReviewResultDTO schema.
    """
    json_data = """
    {
      "summary": "This is a summary of changes.",
      "potential_bugs": [
        {
          "file": "app/db.py",
          "line": "12",
          "level": "MEDIUM",
          "issue": "Connection leaked.",
          "suggestion": "Close the session."
        }
      ],
      "security_issues": [],
      "code_smells": [],
      "performance_issues": [],
      "suggested_test_cases": [],
      "risk_level": "MEDIUM",
      "merge_recommendation": {
        "can_merge": true,
        "reason": "Safe to merge if connection is closed."
      }
    }
    """
    data = json.loads(json_data)
    result = ReviewResultDTO(**data)
    
    assert result.summary == "This is a summary of changes."
    assert len(result.potential_bugs) == 1
    assert result.potential_bugs[0].file == "app/db.py"
    assert result.risk_level == "MEDIUM"
    assert result.merge_recommendation.can_merge is True
