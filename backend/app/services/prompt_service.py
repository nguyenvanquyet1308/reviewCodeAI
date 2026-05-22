from app.prompts.code_review_prompt import CODE_REVIEW_PROMPT_TEMPLATE
from app.prompts.test_generation_prompt import TEST_GENERATION_PROMPT_TEMPLATE

class PromptService:
    @staticmethod
    def get_code_review_prompt(repository_name: str, pr_title: str, diff_text: str) -> str:
        """
        Format the code review prompt template.
        """
        return CODE_REVIEW_PROMPT_TEMPLATE.format(
            repository_name=repository_name,
            pr_title=pr_title,
            diff_text=diff_text
        )

    @staticmethod
    def get_test_generation_prompt(repository_name: str, pr_title: str, diff_text: str) -> str:
        """
        Format the test generation prompt template.
        """
        return TEST_GENERATION_PROMPT_TEMPLATE.format(
            repository_name=repository_name,
            pr_title=pr_title,
            diff_text=diff_text
        )
