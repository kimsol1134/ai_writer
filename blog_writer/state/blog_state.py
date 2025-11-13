from typing import TypedDict, List, Annotated, Optional, Dict, Any
from langgraph.graph import add_messages


class BlogState(TypedDict):
    """블로그 작성 워크플로우 상태"""
    # 입력
    topic: str                          # 블로그 주제
    keywords: List[str]                 # 키워드 목록
    target_length: int                  # 목표 글자 수

    # 조사 단계
    research_data: Optional[str]        # 조사 결과 데이터
    sources: Optional[List[str]]        # 출처 목록

    # 작성 단계
    outline: Optional[str]              # 글 개요
    draft_content: Optional[str]        # 초안

    # 퇴고 단계
    final_content: Optional[str]        # 최종 콘텐츠
    seo_score: Optional[float]          # SEO 점수

    # 워크플로우 제어
    messages: Annotated[list, add_messages]  # 메시지 히스토리
    current_stage: str                  # 현재 단계
    user_feedback: Optional[str]        # 사용자 피드백
    approval_status: Optional[str]      # 승인 상태
    output_file: Optional[str]          # 출력 파일 경로

    # 🆕 되묻기 응답 저장소
    clarifications: Optional[Dict[str, Any]]  # 단계별 되묻기 응답 (research, writing, editing)
