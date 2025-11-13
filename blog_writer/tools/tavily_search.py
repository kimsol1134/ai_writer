from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from tavily import TavilyClient
from typing import Dict


def get_tavily_tool():
    """Lazy initialization of Tavily tool"""
    from blog_writer.config import settings
    return TavilySearchResults(
        max_results=10,
        include_answer=True,
        include_raw_content=True,
        include_images=False,
        api_key=settings.tavily_api_key
    )


# 기본 Tavily 도구 (lazy loading)
tavily_tool = None


# 커스텀 심층 조사 도구
@tool
def deep_research(query: str, max_results: int = 10) -> Dict:
    """주제에 대한 심층 조사 수행"""
    from blog_writer.config import settings
    client = TavilyClient(api_key=settings.tavily_api_key)

    response = client.search(
        query=query,
        search_depth="advanced",  # 심층 검색
        max_results=max_results,
        include_answer=True,
        include_raw_content=True
    )

    # 결과 포맷팅
    formatted_results = {
        "answer": response.get("answer", ""),
        "results": [
            {
                "title": r["title"],
                "url": r["url"],
                "content": r["content"],
                "score": r.get("score", 0)
            }
            for r in response.get("results", [])
        ],
        "query": query
    }

    return formatted_results
