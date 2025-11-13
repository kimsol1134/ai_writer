"""Clarification models for multi-stage user requirements gathering."""

from typing import List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ClarificationQuestion(BaseModel):
    """A single clarification question for the user.

    Attributes:
        text: The question text to display to the user
        category: The category of the question (audience, direction, or constraint)
        placeholder: Placeholder text for the input field
    """
    text: str = Field(..., description="질문 내용")
    category: Literal["audience", "direction", "constraint"] = Field(
        ..., description="질문 카테고리"
    )
    placeholder: str = Field("", description="입력 플레이스홀더")


class ClarificationResponse(BaseModel):
    """Response containing clarification questions and user answers.

    Attributes:
        questions: List of questions that were asked
        answers: List of user's answers corresponding to the questions
        skipped: Whether the user chose to skip this clarification stage
        timestamp: When this response was created
        stage: Which workflow stage this clarification belongs to
    """
    questions: List[ClarificationQuestion]
    answers: List[str]
    skipped: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)
    stage: Literal["research", "writing", "editing"]

    def to_prompt_context(self) -> str:
        """Generate context string to inject into agent prompts.

        Returns:
            A formatted string with Q&A pairs, or empty string if skipped/no answers
        """
        if self.skipped or not self.answers:
            return ""

        context = "\n\n## 📋 사용자 요구사항\n\n"
        for q, a in zip(self.questions, self.answers):
            if a.strip():  # Exclude empty answers
                context += f"**Q: {q.text}**\n답변: {a}\n\n"

        return context

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
