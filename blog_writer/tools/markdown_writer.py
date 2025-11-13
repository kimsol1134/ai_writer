import os
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool
from typing import Optional, Dict, List


@tool
def save_blog_to_markdown(
    content: str,
    topic: str,
    metadata: Optional[Dict] = None,
    output_dir: str = "output"
) -> str:
    """블로그 콘텐츠를 마크다운 파일로 저장 (frontmatter 포함)"""

    # 출력 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_topic = safe_topic.replace(' ', '_')
    filename = f"{timestamp}_{safe_topic}.md"
    filepath = os.path.join(output_dir, filename)

    # Frontmatter 생성
    frontmatter = f"""---
title: "{topic}"
date: {datetime.now().strftime("%Y-%m-%d")}
author: "AI Blog Writer"
generator: "LangGraph v1.0 + Gemini 2.0 Flash"
"""

    if metadata:
        if "keywords" in metadata:
            keywords_str = ", ".join(metadata["keywords"])
            frontmatter += f"keywords: [{keywords_str}]\n"
        if "seo_score" in metadata:
            frontmatter += f"seo_score: {metadata['seo_score']}\n"
        if "word_count" in metadata:
            frontmatter += f"word_count: {metadata['word_count']}\n"

    frontmatter += "---\n\n"

    # 전체 내용 결합
    full_content = frontmatter + content

    # 파일 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    return filepath


@tool
def save_research_notes(
    research_data: str,
    sources: List[str],
    topic: str,
    output_dir: str = "output/research"
) -> str:
    """조사 노트를 별도 파일로 저장"""

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_topic = safe_topic.replace(' ', '_')
    filename = f"{timestamp}_{safe_topic}_research.md"
    filepath = os.path.join(output_dir, filename)

    content = f"""# 조사 노트: {topic}

**작성 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 조사 요약

{research_data}

---

## 참고 자료

"""

    for i, source in enumerate(sources, 1):
        content += f"{i}. {source}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath
