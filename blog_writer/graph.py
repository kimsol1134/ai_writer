from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path
import sqlite3

from langgraph.types import interrupt, Command

from blog_writer.state import BlogState
from blog_writer.config import settings
from blog_writer.agents.research_agent import create_research_agent
from blog_writer.agents.writing_agent import create_writing_agent
from blog_writer.agents.editing_agent import create_editing_agent
from blog_writer.nodes.clarification_nodes import create_clarify_and_approve_node
from blog_writer.tools.markdown_writer import save_blog_to_markdown, save_research_notes


def create_blog_graph(checkpointer=None):
    """블로그 작성 LangGraph 워크플로우 생성"""

    # Agent 초기화
    research_agent = create_research_agent()
    writing_agent = create_writing_agent()
    editing_agent = create_editing_agent()

    # 노드 정의
    def research_node(state: BlogState) -> dict:
        """조사 단계"""
        print("\n" + "="*60)
        print("🔍 1단계: 주제 조사 시작")
        print("="*60)
        result = research_agent(state)

        # 조사 노트 저장
        save_research_notes.invoke({
            "research_data": result["research_data"],
            "sources": result["sources"],
            "topic": state["topic"],
            "output_dir": settings.research_dir
        })

        return result

    def writing_node(state: BlogState) -> dict:
        """작성 단계"""
        print("\n" + "="*60)
        print("✍️ 2단계: 블로그 초안 작성 시작")
        print("="*60)
        return writing_agent(state)

    def editing_node(state: BlogState) -> dict:
        """퇴고 단계"""
        print("\n" + "="*60)
        print("🎨 3단계: 퇴고 및 SEO 최적화 시작")
        print("="*60)
        return editing_agent(state)

    def save_node(state: BlogState) -> dict:
        """최종 저장"""
        print("\n" + "="*60)
        print("💾 최종 단계: 블로그 저장")
        print("="*60)

        filepath = save_blog_to_markdown.invoke({
            "content": state["final_content"],
            "topic": state["topic"],
            "metadata": {
                "keywords": state.get("keywords", []),
                "seo_score": state.get("seo_score", 0),
                "word_count": len(state["final_content"].split())
            },
            "output_dir": settings.output_dir
        })

        print(f"✅ 저장 완료: {filepath}")
        print("="*60 + "\n")

        return {
            "current_stage": "complete",
            "output_file": filepath
        }

    # 🆕 통합 Clarification + Approval 노드 생성
    # 총 4개의 interrupt:
    # 1) research 전: 질문만
    # 2) writing 전: 조사 결과 승인 + 질문
    # 3) editing 전: 초안 승인 + 질문
    # 4) save 전: 최종안 승인만
    research_clarify_and_approve = create_clarify_and_approve_node(
        stage="research",
        content_key=None,  # 연구 전이므로 검토할 콘텐츠 없음
        next_on_approve="research",
        next_on_reject="research_clarify_and_approve"  # 재질문
    )

    writing_clarify_and_approve = create_clarify_and_approve_node(
        stage="writing",
        content_key="research_data",  # 조사 결과 검토 + writing 질문
        next_on_approve="write",
        next_on_reject="research"
    )

    editing_clarify_and_approve = create_clarify_and_approve_node(
        stage="editing",
        content_key="draft_content",  # 초안 검토 + editing 질문
        next_on_approve="edit",
        next_on_reject="write"
    )

    # 최종 승인 노드 (질문 없이 승인만)
    def final_approval_node(state: BlogState) -> Command:
        """최종 콘텐츠 승인"""
        approval_data = {
            "type": "approval",
            "stage": "최종",
            "content": state.get("final_content", ""),
            "seo_score": state.get("seo_score", 0),
            "message": "최종 콘텐츠를 검토해주세요."
        }

        approval_response = interrupt(approval_data)

        if approval_response.get("approved", False):
            return Command(goto="save", update={"approval_status": "approved"})
        else:
            feedback = approval_response.get("feedback", "")
            return Command(
                goto="edit",
                update={
                    "approval_status": "rejected",
                    "user_feedback": feedback
                }
            )

    # 그래프 구성
    builder = StateGraph(BlogState)

    # 노드 추가
    builder.add_node("research_clarify_and_approve", research_clarify_and_approve)
    builder.add_node("research", research_node)
    builder.add_node("writing_clarify_and_approve", writing_clarify_and_approve)
    builder.add_node("write", writing_node)
    builder.add_node("editing_clarify_and_approve", editing_clarify_and_approve)
    builder.add_node("edit", editing_node)
    builder.add_node("final_approval", final_approval_node)
    builder.add_node("save", save_node)

    # 엣지 추가
    builder.set_entry_point("research_clarify_and_approve")
    # research_clarify_and_approve -> research (Command routing)
    builder.add_edge("research", "writing_clarify_and_approve")
    # writing_clarify_and_approve -> write or research (Command routing)
    builder.add_edge("write", "editing_clarify_and_approve")
    # editing_clarify_and_approve -> edit or write (Command routing)
    builder.add_edge("edit", "final_approval")
    # final_approval -> save or edit (Command routing)
    builder.add_edge("save", END)

    # 체크포인터 설정
    if checkpointer is None:
        # SQLite 저장소 생성
        Path("checkpoints").mkdir(exist_ok=True)
        # SqliteSaver 직접 생성 (context manager가 아닌 인스턴스)
        conn = sqlite3.connect(settings.checkpoint_db, check_same_thread=False)
        checkpointer = SqliteSaver(conn)

    # 컴파일
    graph = builder.compile(checkpointer=checkpointer)

    return graph
