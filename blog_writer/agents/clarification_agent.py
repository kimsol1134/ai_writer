"""Clarification agent for generating context-aware questions at each workflow stage."""

import json
from typing import List, Literal

from langchain_google_genai import ChatGoogleGenerativeAI

from blog_writer.models.clarification import ClarificationQuestion
from blog_writer.state import BlogState
from blog_writer.config import settings


# Configure Gemini 2.5 Flash
def _get_gemini_model():
    """Get configured Gemini model instance."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.7
    )


def _build_context_for_stage(
    state: BlogState,
    stage: Literal["research", "writing", "editing"]
) -> str:
    """Build context string based on current stage and state.

    Args:
        state: Current workflow state
        stage: The stage for which to build context

    Returns:
        Formatted context string with relevant state information
    """
    base_context = f"""
- 주제: {state['topic']}
- 키워드: {', '.join(state['keywords'])}
- 목표 길이: {state['target_length']}자
"""

    if stage == "research":
        return base_context + "\n- 단계: 조사 시작 전"

    elif stage == "writing":
        # Include research results summary
        research_summary = state.get('research_data', '')[:200]
        return base_context + f"""
- 단계: 글쓰기 시작 전
- 조사 결과 요약: {research_summary}...
"""

    elif stage == "editing":
        # Include draft summary
        draft_summary = state.get('draft_content', '')[:200]
        return base_context + f"""
- 단계: 퇴고 시작 전
- 초안 요약: {draft_summary}...
"""

    return base_context


def _get_default_questions(
    stage: Literal["research", "writing", "editing"]
) -> List[ClarificationQuestion]:
    """Get default fallback questions for a given stage.

    Args:
        stage: The workflow stage

    Returns:
        List of default questions for the stage
    """
    defaults = {
        "research": [
            ClarificationQuestion(
                text="주요 독자층은 누구인가요?",
                category="audience",
                placeholder="예: 30대 직장인, 초보 부모"
            ),
            ClarificationQuestion(
                text="어떤 정보를 중점적으로 조사해야 할까요?",
                category="direction",
                placeholder="예: 최신 트렌드, 전문가 의견"
            ),
            ClarificationQuestion(
                text="조사 시 피해야 할 출처나 제약사항이 있나요?",
                category="constraint",
                placeholder="예: 특정 사이트 제외"
            ),
        ],
        "writing": [
            ClarificationQuestion(
                text="글의 톤은 어떻게 설정할까요?",
                category="direction",
                placeholder="예: 친근하고 쉽게, 전문적으로"
            ),
            ClarificationQuestion(
                text="특별히 강조하고 싶은 메시지가 있나요?",
                category="direction",
                placeholder="예: 실패 경험 공유"
            ),
            ClarificationQuestion(
                text="피해야 할 표현이나 스타일이 있나요?",
                category="constraint",
                placeholder="예: 이모지 사용 금지"
            ),
        ],
        "editing": [
            ClarificationQuestion(
                text="SEO에서 가장 우선순위를 둘 부분은?",
                category="direction",
                placeholder="예: 키워드 밀도, 메타 설명"
            ),
            ClarificationQuestion(
                text="독자가 가장 먼저 눈여겨볼 부분은 어디일까요?",
                category="audience",
                placeholder="예: 도입부, 실전 팁 섹션"
            ),
            ClarificationQuestion(
                text="퇴고 시 특별히 주의할 점이 있나요?",
                category="constraint",
                placeholder="예: 문장 길이 짧게"
            ),
        ],
    }

    return defaults[stage]


def generate_clarification_questions(
    state: BlogState,
    stage: Literal["research", "writing", "editing"]
) -> List[ClarificationQuestion]:
    """Generate 3-5 clarification questions using Gemini 2.5 Pro.

    Args:
        state: Current workflow state
        stage: The stage for which to generate questions

    Returns:
        List of 3-5 context-aware clarification questions

    Note:
        Falls back to default questions if Gemini API fails
    """
    # Build context for this stage
    context = _build_context_for_stage(state, stage)

    prompt = f"""당신은 블로그 작성 도우미입니다.
사용자가 더 나은 블로그 글을 작성할 수 있도록 **{stage} 단계 시작 전** 필요한 정보를 물어봐야 합니다.

## 현재 컨텍스트
{context}

## 질문 생성 가이드라인
1. **독자 정보**: 누구를 위한 글인가? (전문가/초보자, 연령대, 관심사 등)
2. **콘텐츠 방향**: 어떤 톤/스타일을 원하는가? (전문적/친근한, 학술적/실용적 등)
3. **실용적 제약**: 피해야 할 표현, 강조할 포인트, 특별 요구사항

## 출력 형식 (JSON)
{{
  "questions": [
    {{
      "text": "주요 독자층은 누구인가요? (예: 육아 초보 부모, IT 개발자)",
      "category": "audience",
      "placeholder": "예: 30대 직장인"
    }},
    {{
      "text": "이 글에서 가장 강조하고 싶은 내용은 무엇인가요?",
      "category": "direction",
      "placeholder": "예: 실전 경험 중심"
    }},
    {{
      "text": "피해야 할 표현이나 제약사항이 있나요?",
      "category": "constraint",
      "placeholder": "예: 전문용어 최소화"
    }}
  ]
}}

**중요**: 정확히 3-5개의 질문을 생성하세요. JSON 형식만 출력하세요.
"""

    try:
        model = _get_gemini_model()
        response = model.invoke(prompt)

        # Extract JSON from response
        response_text = response.content.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            # Remove first line (```json or ```)
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])  # Remove first and last line

        # Parse JSON
        questions_data = json.loads(response_text)

        questions = [
            ClarificationQuestion(**q)
            for q in questions_data["questions"]
        ]

        # Validate question count
        if len(questions) < 3 or len(questions) > 5:
            print(f"⚠️ 질문 수가 부적절합니다: {len(questions)}개. 기본 질문 사용")
            return _get_default_questions(stage)

        print(f"✅ {len(questions)}개의 질문 생성 완료 (Gemini 2.5 Flash)")
        return questions

    except Exception as e:
        # Fallback to default questions
        print(f"⚠️ 질문 생성 실패 (Gemini API): {str(e)}. 기본 질문 사용")
        return _get_default_questions(stage)
