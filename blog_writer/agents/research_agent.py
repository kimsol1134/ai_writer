from langchain_google_genai import ChatGoogleGenerativeAI
from blog_writer.config import settings
from blog_writer.state import BlogState
from blog_writer.tools.tavily_search import deep_research
from typing import Dict


def create_research_agent():
    """Tavily 검색 + Gemini 요약 기반 조사 Agent"""

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=0.3,  # 팩트 기반 조사는 낮은 온도
        google_api_key=settings.google_api_key,
        max_retries=settings.max_retries
    )

    def research_node(state: BlogState) -> Dict:
        """주제에 대한 심층 조사 수행"""
        topic = state["topic"]
        keywords = state.get("keywords", [])

        print(f"🔍 주제 조사 중: {topic}")

        # 1. 메인 주제 검색
        main_query = f"{topic} 최신 정보 2025"
        main_results = deep_research.invoke({"query": main_query})

        # 2. 각 키워드별 검색
        keyword_results = []
        for keyword in keywords:
            query = f"{topic} {keyword} 상세 정보"
            results = deep_research.invoke({"query": query})
            keyword_results.append({
                "keyword": keyword,
                "results": results
            })

        # 3. 검색 결과 통합
        all_search_data = f"""# 메인 조사 결과

**쿼리**: {main_query}
**요약**: {main_results.get('answer', 'N/A')}

## 상세 결과

"""
        for i, result in enumerate(main_results.get('results', []), 1):
            all_search_data += f"""
### {i}. {result['title']}
- **출처**: {result['url']}
- **관련도**: {result.get('score', 0):.2f}

{result['content']}

---
"""

        # 키워드별 결과 추가
        for kw_data in keyword_results:
            kw = kw_data['keyword']
            kw_results = kw_data['results']
            all_search_data += f"\n# 키워드 조사: {kw}\n\n"
            all_search_data += f"**요약**: {kw_results.get('answer', 'N/A')}\n\n"

        # 4. 🆕 Clarification 컨텍스트 추출
        clarification_context = ""
        if "clarifications" in state and state.get("clarifications"):
            clarifications = state["clarifications"]
            if "research" in clarifications:
                research_clarif = clarifications["research"]
                # Reconstruct ClarificationResponse to use to_prompt_context
                from blog_writer.models.clarification import ClarificationResponse, ClarificationQuestion
                from datetime import datetime

                clarif_obj = ClarificationResponse(
                    questions=[ClarificationQuestion(**q) for q in research_clarif["questions"]],
                    answers=research_clarif["answers"],
                    skipped=research_clarif["skipped"],
                    timestamp=datetime.fromisoformat(research_clarif["timestamp"]),
                    stage=research_clarif["stage"]
                )
                clarification_context = clarif_obj.to_prompt_context()

        # 5. LLM으로 종합 정리
        synthesis_prompt = f"""당신은 블로그 글을 작성하기 위한 조사 전문가입니다.

아래 검색 결과를 바탕으로 "{topic}"에 대한 블로그 글 작성을 위한 종합 조사 보고서를 작성하세요.

{clarification_context}

## 검색 결과

{all_search_data}

## 요구사항

다음 항목을 포함하여 구조화된 조사 보고서를 작성하세요:

1. **핵심 요약** (3-5문장)
2. **주요 사실과 통계**
3. **최신 트렌드** (2025년 기준)
4. **전문가 의견 및 인용**
5. **구체적인 사례 및 예시**
6. **독자가 알아야 할 핵심 포인트**

보고서는 한글로 작성하고, 블로그 글 작성 시 직접 활용할 수 있도록 명확하고 구조화되어야 합니다.
**위의 사용자 요구사항을 반드시 고려하세요.**
"""

        synthesis_response = llm.invoke(synthesis_prompt)
        synthesized_research = synthesis_response.content

        # 6. 출처 목록 추출
        sources = []
        for result in main_results.get('results', []):
            source = f"[{result['title']}]({result['url']})"
            sources.append(source)

        print(f"✅ 조사 완료: {len(sources)}개 출처 발견")

        return {
            "research_data": synthesized_research,
            "sources": sources,
            "current_stage": "research_complete"
        }

    return research_node
