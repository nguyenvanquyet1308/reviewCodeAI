from app.services.comment_formatter import CommentFormatter
from app.schemas.review_result import ReviewResultDTO, ReviewIssue, SuggestedTestCase, MergeRecommendation

def test_comment_formatter():
    """
    Test that the CommentFormatter constructs the correct markdown layout
    with proper tables and sections from a ReviewResultDTO object.
    """
    result = ReviewResultDTO(
        summary="Code looks great overall.",
        potential_bugs=[
            ReviewIssue(
                file="main.py",
                line="10",
                level="HIGH",
                issue="Division by zero.",
                suggestion="Check if divisor is zero."
            )
        ],
        security_issues=[],
        code_smells=[
            ReviewIssue(
                file="utils.py",
                line="50",
                level="LOW",
                issue="Too many nested loops.",
                suggestion="Simplify logic."
            )
        ],
        performance_issues=[],
        suggested_test_cases=[
            SuggestedTestCase(
                name="Test divisor is zero",
                description="Verify handling when division is attempted by zero.",
                priority="HIGH"
            )
        ],
        risk_level="MEDIUM",
        merge_recommendation=MergeRecommendation(
            can_merge=True,
            reason="Minor issue that can be fixed post-merge."
        )
    )
    
    comment = CommentFormatter.format_comment(result)
    
    assert "## AI Code Review Result" in comment
    assert "### Potential Bugs" in comment
    assert "main.py" in comment
    assert "Division by zero." in comment
    assert "### Security Issues" in comment
    assert "_Không phát hiện vấn đề rõ ràng._" in comment
    assert "### Code Smells" in comment
    assert "Too many nested loops." in comment
    assert "### Suggested Test Cases" in comment
    assert "Test divisor is zero" in comment
    assert "**Can merge:** Yes" in comment
