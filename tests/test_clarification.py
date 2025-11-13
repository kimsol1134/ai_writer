"""Unit tests for clarification system."""

import pytest
from datetime import datetime
from blog_writer.models.clarification import (
    ClarificationQuestion,
    ClarificationResponse
)
from blog_writer.agents.clarification_agent import (
    _get_default_questions,
    _build_context_for_stage
)


class TestClarificationModels:
    """Test clarification data models."""

    def test_clarification_question_creation(self):
        """Test creating a clarification question."""
        question = ClarificationQuestion(
            text="주요 독자층은 누구인가요?",
            category="audience",
            placeholder="예: 30대 직장인"
        )

        assert question.text == "주요 독자층은 누구인가요?"
        assert question.category == "audience"
        assert question.placeholder == "예: 30대 직장인"

    def test_clarification_response_creation(self):
        """Test creating a clarification response."""
        questions = [
            ClarificationQuestion(
                text="독자는?",
                category="audience",
                placeholder=""
            )
        ]
        answers = ["30대 직장인"]

        response = ClarificationResponse(
            questions=questions,
            answers=answers,
            skipped=False,
            stage="research"
        )

        assert len(response.questions) == 1
        assert len(response.answers) == 1
        assert response.skipped is False
        assert response.stage == "research"
        assert isinstance(response.timestamp, datetime)

    def test_clarification_skip(self):
        """Test skipped clarification response."""
        response = ClarificationResponse(
            questions=[],
            answers=[],
            skipped=True,
            stage="research"
        )

        context = response.to_prompt_context()
        assert context == ""  # Skipped should return empty context

    def test_prompt_context_generation(self):
        """Test generating prompt context from clarification response."""
        questions = [
            ClarificationQuestion(
                text="독자는?",
                category="audience",
                placeholder=""
            ),
            ClarificationQuestion(
                text="톤은?",
                category="direction",
                placeholder=""
            )
        ]
        answers = ["30대 직장인", "친근하게"]

        response = ClarificationResponse(
            questions=questions,
            answers=answers,
            skipped=False,
            stage="research"
        )

        context = response.to_prompt_context()

        assert "독자는?" in context
        assert "30대 직장인" in context
        assert "톤은?" in context
        assert "친근하게" in context
        assert "사용자 요구사항" in context

    def test_empty_answers_filtered(self):
        """Test that empty answers are filtered out."""
        questions = [
            ClarificationQuestion(text="Q1", category="audience", placeholder=""),
            ClarificationQuestion(text="Q2", category="direction", placeholder="")
        ]
        answers = ["Answer 1", ""]  # Second answer is empty

        response = ClarificationResponse(
            questions=questions,
            answers=answers,
            skipped=False,
            stage="research"
        )

        context = response.to_prompt_context()

        assert "Q1" in context
        assert "Answer 1" in context
        assert "Q2" not in context  # Empty answer should be filtered


class TestDefaultQuestions:
    """Test default fallback questions."""

    def test_default_research_questions(self):
        """Test default questions for research stage."""
        questions = _get_default_questions("research")

        assert len(questions) == 3
        assert all(isinstance(q, ClarificationQuestion) for q in questions)
        assert any(q.category == "audience" for q in questions)
        assert any(q.category == "direction" for q in questions)
        assert any(q.category == "constraint" for q in questions)

    def test_default_writing_questions(self):
        """Test default questions for writing stage."""
        questions = _get_default_questions("writing")

        assert len(questions) == 3
        assert all(isinstance(q, ClarificationQuestion) for q in questions)

    def test_default_editing_questions(self):
        """Test default questions for editing stage."""
        questions = _get_default_questions("editing")

        assert len(questions) == 3
        assert all(isinstance(q, ClarificationQuestion) for q in questions)

    def test_all_default_questions_have_placeholders(self):
        """Test that all default questions have placeholders."""
        for stage in ["research", "writing", "editing"]:
            questions = _get_default_questions(stage)
            for q in questions:
                assert q.placeholder != ""
                assert q.text != ""


class TestContextBuilding:
    """Test context building for different stages."""

    def test_research_context(self):
        """Test context building for research stage."""
        state = {
            "topic": "AI in healthcare",
            "keywords": ["machine learning", "diagnosis"],
            "target_length": 2000
        }

        context = _build_context_for_stage(state, "research")

        assert "AI in healthcare" in context
        assert "machine learning" in context
        assert "diagnosis" in context
        assert "2000" in context
        assert "조사 시작 전" in context

    def test_writing_context(self):
        """Test context building for writing stage."""
        state = {
            "topic": "AI in healthcare",
            "keywords": ["machine learning"],
            "target_length": 2000,
            "research_data": "This is research data about AI in healthcare and how it helps doctors..."
        }

        context = _build_context_for_stage(state, "writing")

        assert "AI in healthcare" in context
        assert "글쓰기 시작 전" in context
        assert "This is research data" in context

    def test_editing_context(self):
        """Test context building for editing stage."""
        state = {
            "topic": "AI in healthcare",
            "keywords": ["machine learning"],
            "target_length": 2000,
            "draft_content": "This is a draft about AI in healthcare..."
        }

        context = _build_context_for_stage(state, "editing")

        assert "AI in healthcare" in context
        assert "퇴고 시작 전" in context
        assert "This is a draft" in context

    def test_missing_optional_fields(self):
        """Test context building with missing optional fields."""
        state = {
            "topic": "Test topic",
            "keywords": [],
            "target_length": 1000
        }

        # Should not raise error even without research_data or draft_content
        context_research = _build_context_for_stage(state, "research")
        context_writing = _build_context_for_stage(state, "writing")
        context_editing = _build_context_for_stage(state, "editing")

        assert "Test topic" in context_research
        assert "Test topic" in context_writing
        assert "Test topic" in context_editing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
