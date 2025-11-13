from langgraph.types import interrupt, Command
from blog_writer.state import BlogState
from typing import Literal, Union


def create_approval_node(stage_name: str, next_on_approve: str, next_on_reject: str):
    """범용 승인 노드 생성기"""

    def approval_node(state: BlogState) -> Command[Literal[next_on_approve, next_on_reject]]:
        """사용자 승인 대기"""

        # 승인 요청 데이터 준비
        approval_data = {
            "stage": stage_name,
            "message": f"{stage_name} 단계 검토가 필요합니다.",
        }

        # 단계별 표시 데이터 추가
        if stage_name == "조사":
            approval_data["research_data"] = state.get("research_data", "")
            approval_data["sources"] = state.get("sources", [])
        elif stage_name == "초안":
            approval_data["outline"] = state.get("outline", "")
            approval_data["draft_content"] = state.get("draft_content", "")
        elif stage_name == "최종":
            approval_data["final_content"] = state.get("final_content", "")
            approval_data["seo_score"] = state.get("seo_score", 0)

        # 인터럽트 발생 및 사용자 응답 대기
        user_response = interrupt(approval_data)

        # 응답 처리
        if isinstance(user_response, dict):
            approved = user_response.get("approved", False)
            feedback = user_response.get("feedback", "")

            if approved:
                return Command(
                    update={"approval_status": "approved"},
                    goto=next_on_approve
                )
            else:
                return Command(
                    update={
                        "approval_status": "rejected",
                        "user_feedback": feedback
                    },
                    goto=next_on_reject
                )
        else:
            # 단순 boolean 응답
            if user_response:
                return Command(goto=next_on_approve)
            else:
                return Command(goto=next_on_reject)

    return approval_node
