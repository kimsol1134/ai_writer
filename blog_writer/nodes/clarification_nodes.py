"""Unified clarification and approval nodes for workflow stages."""

from typing import Literal, Optional
from datetime import datetime

from langgraph.types import interrupt, Command

from blog_writer.state import BlogState
from blog_writer.agents.clarification_agent import generate_clarification_questions
from blog_writer.models.clarification import ClarificationResponse


def create_clarify_and_approve_node(
    stage: Literal["research", "writing", "editing"],
    content_key: Optional[str],
    next_on_approve: str,
    next_on_reject: str
):
    """Create a unified clarification + approval node for a workflow stage.

    This node performs two steps in sequence:
    1. If content exists, show it for approval (skip for research stage)
    2. Generate clarification questions for the next stage

    Args:
        stage: The workflow stage name
        content_key: State key containing content to review (None for research)
        next_on_approve: Next node to goto on approval
        next_on_reject: Next node to goto on rejection

    Returns:
        A node function that handles both approval and clarification
    """

    def clarify_and_approve_node(state: BlogState) -> Command:
        """Unified clarification and approval node.

        Returns:
            Command with state updates and routing information
        """
        # Step 1: Content Review (skip for research stage)
        if content_key and content_key in state and state.get(content_key):
            # Content exists, request approval first
            approval_data = {
                "type": "approval",
                "stage": stage,
                "content": state[content_key],
                "message": f"{stage} 단계 결과를 검토해주세요."
            }

            # Add stage-specific data
            if stage == "research":
                approval_data["sources"] = state.get("sources", [])
            elif stage == "writing":
                approval_data["outline"] = state.get("outline", "")
            elif stage == "editing":
                approval_data["seo_score"] = state.get("seo_score", 0)

            approval_response = interrupt(approval_data)

            # Check approval
            if not approval_response.get("approved", False):
                # Rejected - go back to previous stage
                feedback = approval_response.get("feedback", "")
                return Command(
                    goto=next_on_reject,
                    update={
                        "approval_status": "rejected",
                        "user_feedback": feedback
                    }
                )

        # Step 2: Clarification Questions
        print(f"\n🤔 {stage.upper()} 단계 질문 생성 중...")

        # Generate questions using Gemini
        questions = generate_clarification_questions(state, stage)

        clarification_data = {
            "type": "clarification",
            "stage": stage,
            "questions": [q.model_dump() for q in questions],
            "message": f"{stage} 단계를 시작하기 전 몇 가지 질문드립니다."
        }

        clarification_response = interrupt(clarification_data)

        # Process clarification response
        answers = clarification_response.get("answers", [])
        skipped = clarification_response.get("skipped", False)

        # Create clarification response object
        clarification = ClarificationResponse(
            questions=questions,
            answers=answers,
            skipped=skipped,
            timestamp=datetime.now(),
            stage=stage
        )

        # Update state
        clarifications = state.get("clarifications", {})
        if clarifications is None:
            clarifications = {}

        # Convert ClarificationResponse to dict for state storage
        clarifications[stage] = {
            "questions": [q.model_dump() for q in clarification.questions],
            "answers": clarification.answers,
            "skipped": clarification.skipped,
            "timestamp": clarification.timestamp.isoformat(),
            "stage": clarification.stage
        }

        print(f"✅ 질문 응답 저장 완료 (skipped: {skipped})")

        # Proceed to next stage
        return Command(
            goto=next_on_approve,
            update={
                "clarifications": clarifications,
                "approval_status": "approved"
            }
        )

    return clarify_and_approve_node
