from langchain_google_genai import ChatGoogleGenerativeAI
from blog_writer.config import settings
from blog_writer.state import BlogState
from typing import Dict


def create_writing_agent():
    """조사 결과 기반 블로그 초안 작성 Agent"""

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=0.7,  # 창의적 글쓰기는 중간 온도
        google_api_key=settings.google_api_key,
        max_retries=settings.max_retries
    )

    def writing_node(state: BlogState) -> Dict:
        """조사 데이터를 바탕으로 블로그 초안 작성"""
        topic = state["topic"]
        research = state["research_data"]
        keywords = state.get("keywords", [])
        target_length = state.get("target_length", 2000)

        print(f"✍️ 블로그 초안 작성 중: {topic}")

        # 커스텀 작성 스타일 가져오기
        custom_style = settings.writing_style

        # 🆕 Clarification 컨텍스트 추출
        clarification_context = ""
        if "clarifications" in state and state.get("clarifications"):
            clarifications = state["clarifications"]
            if "writing" in clarifications:
                writing_clarif = clarifications["writing"]
                # Reconstruct ClarificationResponse to use to_prompt_context
                from blog_writer.models.clarification import ClarificationResponse, ClarificationQuestion
                from datetime import datetime

                clarif_obj = ClarificationResponse(
                    questions=[ClarificationQuestion(**q) for q in writing_clarif["questions"]],
                    answers=writing_clarif["answers"],
                    skipped=writing_clarif["skipped"],
                    timestamp=datetime.fromisoformat(writing_clarif["timestamp"]),
                    stage=writing_clarif["stage"]
                )
                clarification_context = clarif_obj.to_prompt_context()

        # 1. 개요(Outline) 작성
        outline_prompt = f"""당신은 전문 블로그 작가입니다.

아래 조사 결과를 바탕으로 "{topic}"에 대한 블로그 글의 상세한 개요를 작성하세요.

{clarification_context}

## 조사 자료

{research}

## 작성 스타일 가이드

{custom_style}

## 요구사항

1. **매력적인 제목** (위 스타일 가이드의 제목 패턴 참고)
2. **도입부 구성** (생생한 일화나 충격적 장면으로 시작)
3. **본문 섹션** (개인 경험 + 전문 지식 결합)
   - 각 섹션마다 구체적인 숫자/통계 포함
   - 실패 경험과 공감 표현
4. **결론 구성** (실용적인 액션 아이템 + 격려 메시지)

목표 길이: 약 {target_length}자
키워드: {', '.join(keywords)}

**반드시 위의 작성 스타일을 따라주세요.**
"""

        outline_response = llm.invoke(outline_prompt)
        outline = outline_response.content

        print(f"📝 개요 작성 완료")

        # 2. 전체 초안 작성
        draft_prompt = f"""당신은 전문 블로그 작가입니다.

아래 개요와 조사 자료를 바탕으로 완성된 블로그 글을 작성하세요.

{clarification_context}

## 개요

{outline}

## 조사 자료

{research}

## 작성 스타일 가이드 (엄격히 준수)

{custom_style}

## 작성 요구사항

1. **길이**: 약 {target_length}자
2. **구조**:
   - 마크다운 형식 사용
   - 헤더(##, ###) 활용하여 섹션 구분
   - **굵은 글씨**와 *기울임꼴* 적절히 활용
3. **내용**:
   - 구체적인 예시와 데이터 포함
   - 독자에게 실질적인 가치 제공
   - 자연스럽게 키워드 포함: {', '.join(keywords)}
4. **스타일 준수**:
   - 위의 "작성 스타일 가이드"를 반드시 따르세요
   - 평어체 (~했다, ~다) 사용
   - 대화형 질문 던지기
   - 솔직한 표현 사용
   - 리스트 최소화, 스토리텔링 중심

한국어로 작성하세요.
"""

        draft_response = llm.invoke(draft_prompt)
        draft = draft_response.content

        print(f"✅ 초안 작성 완료 ({len(draft.split())}단어)")

        return {
            "outline": outline,
            "draft_content": draft,
            "current_stage": "draft_complete"
        }

    return writing_node
