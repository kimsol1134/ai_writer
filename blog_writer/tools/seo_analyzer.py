from langchain_core.tools import tool
from typing import List, Dict


@tool
def calculate_seo_score(content: str, keywords: List[str]) -> Dict:
    """SEO 점수 계산"""
    word_count = len(content.split())

    # 키워드 밀도 계산
    keyword_counts = {
        kw: content.lower().count(kw.lower())
        for kw in keywords
    }
    keyword_density = {
        kw: (count / word_count) * 100 if word_count > 0 else 0
        for kw, count in keyword_counts.items()
    }

    # 가독성 계산
    sentences = content.count('.') + content.count('!') + content.count('?')
    avg_sentence_length = word_count / max(sentences, 1)

    # 헤더 개수
    h2_count = content.count('## ')
    h3_count = content.count('### ')
    total_headers = h2_count + h3_count

    # 점수 계산 (100점 만점)
    score = 0
    recommendations = []

    # 글자 수 (30점)
    if 1500 <= word_count <= 3000:
        score += 30
    elif word_count < 1500:
        recommendations.append(f"글이 짧습니다. 현재 {word_count}자, 최소 1500자 권장")
    else:
        recommendations.append(f"글이 너무 깁니다. 현재 {word_count}자, 최대 3000자 권장")

    # 키워드 밀도 (30점)
    good_density = all(0.5 <= d <= 2.5 for d in keyword_density.values())
    if good_density:
        score += 30
    else:
        for kw, density in keyword_density.items():
            if density < 0.5:
                recommendations.append(f"키워드 '{kw}' 사용 빈도 증가 필요 (현재 {density:.2f}%)")
            elif density > 2.5:
                recommendations.append(f"키워드 '{kw}' 과다 사용 (현재 {density:.2f}%)")

    # 가독성 (20점)
    if 15 <= avg_sentence_length <= 25:
        score += 20
    else:
        recommendations.append(f"문장 길이 조정 필요 (평균 {avg_sentence_length:.1f}단어)")

    # 구조화 (20점)
    if h2_count >= 3:
        score += 10
    else:
        recommendations.append(f"H2 헤더 추가 필요 (현재 {h2_count}개, 최소 3개)")

    if h3_count >= 5:
        score += 10
    else:
        recommendations.append(f"H3 헤더 추가 필요 (현재 {h3_count}개, 최소 5개)")

    return {
        "score": score,
        "word_count": word_count,
        "keyword_density": keyword_density,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "header_count": total_headers,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "recommendations": recommendations
    }
