TEST_GENERATION_PROMPT_TEMPLATE = """Bạn là Senior Test Engineer. Hãy tạo các test case chi tiết cho code diff dưới đây:

Thông tin PR:
Repository: {repository_name}
Pull Request title: {pr_title}

Code diff:
{diff_text}

Hãy trả về danh sách các test case cần bổ sung dưới định dạng JSON:
[
  {
    "name": "string",
    "description": "string",
    "priority": "LOW | MEDIUM | HIGH"
  }
]
"""
