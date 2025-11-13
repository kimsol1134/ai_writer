from langchain_google_genai import ChatGoogleGenerativeAI
from blog_writer.config import settings
from blog_writer.state import BlogState
from blog_writer.tools.seo_analyzer import calculate_seo_score
from typing import Dict


def create_editing_agent():
    """SEO 최적화 및 퇴고 Agent"""

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=0.5,  # 퇴고는 중간 온도
        google_api_key=settings.google_api_key,
        max_retries=settings.max_retries
    )

    def editing_node(state: BlogState) -> Dict:
        """초안을 퇴고하고 SEO 최적화"""
        draft = state["draft_content"]
        keywords = state.get("keywords", [])
        topic = state["topic"]

        print(f"🎨 퇴고 및 SEO 최적화 중...")

        # 1. 초기 SEO 점수 계산
        initial_seo = calculate_seo_score.invoke({
            "content": draft,
            "keywords": keywords
        })

        print(f"📊 초기 SEO 점수: {initial_seo['score']}/100")

        # 2. 🆕 Clarification 컨텍스트 추출
        clarification_context = ""
        if "clarifications" in state and state.get("clarifications"):
            clarifications = state["clarifications"]
            if "editing" in clarifications:
                editing_clarif = clarifications["editing"]
                # Reconstruct ClarificationResponse to use to_prompt_context
                from blog_writer.models.clarification import ClarificationResponse, ClarificationQuestion
                from datetime import datetime

                clarif_obj = ClarificationResponse(
                    questions=[ClarificationQuestion(**q) for q in editing_clarif["questions"]],
                    answers=editing_clarif["answers"],
                    skipped=editing_clarif["skipped"],
                    timestamp=datetime.fromisoformat(editing_clarif["timestamp"]),
                    stage=editing_clarif["stage"]
                )
                clarification_context = clarif_obj.to_prompt_context()

        # 3. 퇴고 및 개선
        edit_prompt = f"""당신은 전문 에디터이자 SEO 전문가입니다.

아래 블로그 초안을 검토하고 개선하세요.

{clarification_context}

## 초안

{draft}

## 현재 SEO 분석

- **점수**: {initial_seo['score']}/100
- **글자 수**: {initial_seo['word_count']}자
- **키워드 밀도**: {initial_seo['keyword_density']}
- **평균 문장 길이**: {initial_seo['avg_sentence_length']}단어
- **헤더 수**: H2 {initial_seo['h2_count']}개, H3 {initial_seo['h3_count']}개

## 개선 권장사항

{chr(10).join('- ' + rec for rec in initial_seo['recommendations'])}

## 퇴고 작업

다음 사항을 개선하여 최종 버전을 작성하세요:

1. **문법 및 맞춤법**: 오류 수정
2. **가독성**: 문장 길이와 흐름 개선
3. **SEO 최적화**:
   - 키워드 자연스럽게 배치 (과도하지 않게)
   - H2, H3 헤더 적절히 추가
   - 메타 설명에 적합한 도입부 작성
4. **구조**: 마크다운 형식 유지 및 개선
5. **내용**: 명확성과 깊이 향상

네이버 블로그 SEO를 고려하여 최종 버전을 작성하세요.
마크다운 형식을 유지하고, 한국어로 작성하세요.
"""

        edited_response = llm.invoke(edit_prompt)
        final_content = edited_response.content

        # 4. 최종 SEO 점수 계산
        final_seo = calculate_seo_score.invoke({
            "content": final_content,
            "keywords": keywords
        })

        print(f"📊 최종 SEO 점수: {final_seo['score']}/100 (개선: +{final_seo['score'] - initial_seo['score']}점)")

        return {
            "final_content": final_content,
            "seo_score": final_seo["score"],
            "current_stage": "editing_complete"
        }

    return editing_node
