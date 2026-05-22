import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.core.exceptions import AIReviewException
from app.schemas.review_result import ReviewResultDTO, ReviewIssue, SuggestedTestCase, MergeRecommendation
from app.services.prompt_service import PromptService

logger = logging.getLogger("ai_review_platform")

class AIReviewService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY is not set. AI review service will run in MOCK mode.")

    def review_pull_request(self, diff_text: str, repository_name: str, pr_title: str) -> ReviewResultDTO:
        """
        Review a Pull Request diff. Splits it into chunks if it is too long,
        reviews each chunk, and synthesizes the results.
        """
        if not self.api_key:
            return self._generate_mock_review(repository_name, pr_title)

        if not diff_text.strip():
            return ReviewResultDTO(
                summary="Không có thay đổi nào được phát hiện trong PR này.",
                potential_bugs=[],
                security_issues=[],
                code_smells=[],
                performance_issues=[],
                suggested_test_cases=[],
                risk_level="LOW",
                merge_recommendation=MergeRecommendation(can_merge=True, reason="Không có thay đổi để review.")
            )

        max_chars = settings.MAX_DIFF_CHARS
        if len(diff_text) <= max_chars:
            logger.info(f"Diff length ({len(diff_text)} chars) is within limit. Running single-pass AI review.")
            return self._run_single_pass_review(diff_text, repository_name, pr_title)
        else:
            logger.info(f"Diff length ({len(diff_text)} chars) exceeds limit of {max_chars}. Running multi-pass chunked review.")
            return self._run_chunked_review(diff_text, repository_name, pr_title, max_chars)

    def _run_single_pass_review(self, diff_text: str, repository_name: str, pr_title: str) -> ReviewResultDTO:
        prompt = PromptService.get_code_review_prompt(repository_name, pr_title, diff_text)
        
        try:
            # Using Structured Outputs (beta.chat.completions.parse)
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful software engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format=ReviewResultDTO,
                timeout=90.0
            )
            parsed_result = completion.choices[0].message.parsed
            if parsed_result is None:
                # Fallback if parsing fails internally
                raise AIReviewException("Failed to parse structured output from OpenAI.")
            return parsed_result
        except Exception as e:
            logger.error(f"Error during single-pass AI review: {str(e)}")
            # Attempt a standard JSON fallback
            return self._fallback_json_completion(prompt)

    def _fallback_json_completion(self, prompt: str) -> ReviewResultDTO:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful software engineering assistant. You must return valid JSON matching the requested schema."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                timeout=90.0
            )
            content = completion.choices[0].message.content
            data = json.loads(content)
            return ReviewResultDTO(**data)
        except Exception as e:
            logger.error(f"Fallback JSON completion failed: {str(e)}")
            raise AIReviewException(f"AI service was unable to generate a valid review: {str(e)}")

    def _run_chunked_review(self, diff_text: str, repository_name: str, pr_title: str, max_chars: int) -> ReviewResultDTO:
        # Split diff into chunks per file
        chunks = []
        current_chunk = []
        for line in diff_text.splitlines():
            if line.startswith("diff --git "):
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
            current_chunk.append(line)
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        # Group chunks to maximize chunk sizes below max_chars
        grouped_diffs = []
        current_group = []
        current_len = 0
        for chunk in chunks:
            chunk_len = len(chunk)
            if chunk_len > max_chars:
                if current_group:
                    grouped_diffs.append("\n".join(current_group))
                    current_group = []
                    current_len = 0
                # Truncate single extremely large file diff
                grouped_diffs.append(chunk[:max_chars])
            elif current_len + chunk_len > max_chars:
                grouped_diffs.append("\n".join(current_group))
                current_group = [chunk]
                current_len = chunk_len
            else:
                current_group.append(chunk)
                current_len += chunk_len
        if current_group:
            grouped_diffs.append("\n".join(current_group))

        logger.info(f"Split PR diff into {len(grouped_diffs)} chunk groups for processing.")

        # Review each chunk
        partial_reviews = []
        for idx, sub_diff in enumerate(grouped_diffs):
            logger.info(f"Reviewing chunk {idx+1}/{len(grouped_diffs)}")
            try:
                review_part = self._run_single_pass_review(
                    sub_diff, repository_name, f"{pr_title} (Part {idx+1}/{len(grouped_diffs)})"
                )
                partial_reviews.append(review_part)
            except Exception as e:
                logger.error(f"Failed to review chunk {idx+1}: {str(e)}")
                # Continue with other chunks if possible

        if not partial_reviews:
            raise AIReviewException("Failed to review all chunks of the PR.")

        # Synthesize results
        return self._synthesize_partial_reviews(partial_reviews, repository_name, pr_title)

    def _synthesize_partial_reviews(self, partial_reviews: List[ReviewResultDTO], repository_name: str, pr_title: str) -> ReviewResultDTO:
        logger.info("Synthesizing partial reviews...")
        
        # Accumulate issues
        bugs = []
        security = []
        smells = []
        performance = []
        test_cases = []
        summaries = []

        for idx, part in enumerate(partial_reviews):
            bugs.extend(part.potential_bugs)
            security.extend(part.security_issues)
            smells.extend(part.code_smells)
            performance.extend(part.performance_issues)
            test_cases.extend(part.suggested_test_cases)
            summaries.append(f"Part {idx+1} Summary: {part.summary}")

        # Construct synthesis payload
        synthesis_input = {
            "partial_summaries": summaries,
            "bugs_count": len(bugs),
            "security_count": len(security),
            "smells_count": len(smells),
            "performance_count": len(performance),
            "test_cases_count": len(test_cases)
        }

        synthesis_prompt = f"""Bạn là Senior Software Engineer. Hãy tổng hợp các review từng phần dưới đây của một Pull Request thành một báo cáo tổng hợp duy nhất.

Thông tin PR:
Repository: {repository_name}
Pull Request title: {pr_title}

Các tóm tắt từng phần:
{json.dumps(synthesis_input["partial_summaries"], indent=2, ensure_ascii=False)}

Hãy tạo ra một JSON phản hồi tổng hợp khớp với schema quy định:
- 'summary': Tóm tắt ngắn gọn toàn bộ PR (1-2 đoạn văn).
- 'risk_level': Đánh giá rủi ro chung (LOW, MEDIUM, HIGH) dựa trên tổng hợp lỗi.
- 'merge_recommendation': Đưa ra khuyến nghị merge (can_merge: true/false và lý do).

Trả về JSON hợp lệ theo schema:
{{
  "summary": "string",
  "risk_level": "LOW | MEDIUM | HIGH",
  "merge_recommendation": {{
    "can_merge": true,
    "reason": "string"
  }}
}}
"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful software engineering assistant."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                response_format={"type": "json_object"},
                timeout=60.0
            )
            synth_data = json.loads(completion.choices[0].message.content)
            
            return ReviewResultDTO(
                summary=synth_data.get("summary", "Đã hoàn thành review."),
                potential_bugs=bugs,
                security_issues=security,
                code_smells=smells,
                performance_issues=performance,
                suggested_test_cases=test_cases,
                risk_level=synth_data.get("risk_level", "MEDIUM"),
                merge_recommendation=MergeRecommendation(
                    can_merge=synth_data.get("merge_recommendation", {}).get("can_merge", True),
                    reason=synth_data.get("merge_recommendation", {}).get("reason", "Không có lý do từ chối rõ ràng.")
                )
            )
        except Exception as e:
            logger.error(f"Error during review synthesis: {str(e)}")
            # Basic fallback compilation
            has_high_risk = any(b.level == "HIGH" for b in bugs) or any(s.level == "HIGH" for s in security)
            risk = "HIGH" if has_high_risk else "MEDIUM" if (bugs or security) else "LOW"
            return ReviewResultDTO(
                summary=" / ".join(summaries),
                potential_bugs=bugs,
                security_issues=security,
                code_smells=smells,
                performance_issues=performance,
                suggested_test_cases=test_cases,
                risk_level=risk,
                merge_recommendation=MergeRecommendation(
                    can_merge=not has_high_risk,
                    reason="Tự động duyệt do có lỗi xảy ra khi tổng hợp bằng AI." if has_high_risk else "Không có rủi ro nghiêm trọng."
                )
            )

    def _generate_mock_review(self, repository_name: str, pr_title: str) -> ReviewResultDTO:
        """
        Generates a beautiful mock review result when no OpenAI API key is present.
        """
        logger.info("Generating mock AI code review...")
        return ReviewResultDTO(
            summary=f"Đây là kết quả review MOCK cho Pull Request: '{pr_title}' trên repo '{repository_name}'. Hệ thống đang hoạt động ở chế độ development (không có OpenAI API key).",
            potential_bugs=[
                ReviewIssue(
                    file="app/main.py",
                    line="15",
                    level="MEDIUM",
                    issue="Không xử lý ngoại lệ khi kết nối Database.",
                    suggestion="Nên bao bọc kết nối trong khối try-except và ghi log chi tiết."
                )
            ],
            security_issues=[
                ReviewIssue(
                    file="docker-compose.yml",
                    line="8",
                    level="HIGH",
                    issue="Password của database PostgreSQL đang được ghi trực tiếp (hardcode).",
                    suggestion="Nên chuyển password thành biến môi trường thông qua file .env."
                )
            ],
            code_smells=[
                ReviewIssue(
                    file="app/services/ai_review_service.py",
                    line="125",
                    level="LOW",
                    issue="Hàm _generate_mock_review quá dài và có nhiều thông tin hardcode.",
                    suggestion="Có thể tách hàm hoặc đọc dữ liệu mock từ file JSON cấu hình."
                )
            ],
            performance_issues=[
                ReviewIssue(
                    file="app/db/session.py",
                    line="4",
                    level="LOW",
                    issue="Không sử dụng Connection Pool hiệu quả.",
                    suggestion="Đảm bảo pool_size được thiết lập tối ưu cho tải ứng dụng."
                )
            ],
            suggested_test_cases=[
                SuggestedTestCase(
                    name="Test DB Connection Failure",
                    description="Xác minh ứng dụng xử lý trơn tru khi cơ sở dữ liệu ngắt kết nối.",
                    priority="MEDIUM"
                ),
                SuggestedTestCase(
                    name="Test Webhook Signature Bypass Attempt",
                    description="Xác minh hệ thống trả về mã lỗi 401 khi chữ ký webhook không hợp lệ.",
                    priority="HIGH"
                )
            ],
            risk_level="HIGH",
            merge_recommendation=MergeRecommendation(
                can_merge=False,
                reason="Phát hiện lỗi bảo mật nghiêm trọng (hardcoded password) và thiếu xử lý ngoại lệ cơ sở dữ liệu."
            )
        )
