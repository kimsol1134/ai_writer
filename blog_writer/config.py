from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정 (환경 변수에서 자동 로드)"""

    # API 키
    google_api_key: str = ""
    tavily_api_key: str = ""
    langsmith_api_key: Optional[str] = None
    langsmith_tracing: Optional[bool] = False

    # 모델 설정
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_retries: int = 2

    # 애플리케이션 설정
    checkpoint_db: str = "checkpoints/blog_workflows.sqlite"
    output_dir: str = "output"
    research_dir: str = "output/research"
    log_level: str = "INFO"

    # 커스텀 작성 스타일
    writing_style: str = """
**내 작성 스타일 DNA:**
1. 전문 지식을 스토리로 풀어냄
2. 데이터로 신뢰를 주고 감성으로 연결
3. 실패를 솔직히 공유하며 공감대 형성
4. 항상 실용적인 액션 아이템 제공

**구조 (SUCCES 프레임워크):**

【도입부 - Hook & Problem】
- 생생한 일화/충격적 장면으로 시작 (처음 3줄이 승부)
- 예: "새벽 1시, 고속도로를 달리는데 순찰차가 저를 멈춰 세웠다..."
- 독자가 공감할 문제 상황 제시

【본론 - Solution & Evidence】
- 개인 경험 + 전문 지식 결합
- 구체적 숫자/통계 인용 (93%, 14일, 900대 1 등)
- 단계별 과정 상세 설명
- "나도 그랬다", "정말 힘들었다" 공감 표현

【결론 - Emotion & Action】
- "배운 것들" 자연스럽게 풀어서 정리
- 체크리스트나 실전 팁 제공
- 독자에게 희망과 격려의 메시지

**문체 원칙:**
- 평어체 (~했다, ~다) 사용
- 대화형 질문 던지기 ("~일까?", "놀랍지 않나요?")
- 솔직한 표현 ("쫄아서", "겨우겨우", "제대로 실패했다")
- 리스트 최소화, 줄글 스토리텔링 중심

**제목 패턴 (선택 하나):**
□ 질문형: "우리 집 자산 관리, 더 쉽게 할 수 없을까?"
□ 숫자+구체성: "93%의 부모가 실패하는 밥 전쟁, 14일 만에 끝낸 방법"
□ 감성형: "길이 없으면 만들어서 간다 - 초자기주도력을 되찾은 이야기"
□ 전문성 강조: "[응급의 아빠] 열성경련 대처법 완전정복"

**차별화 포인트:**
- "외과전문의 + 응급실근무경험 + 아빠" 정체성 (의사 + 아빠)
- 전문 데이터 + 따뜻한 스토리
- 실패담도 솔직하게 공유

**금지 사항:**
- 존댓말 (습니다, ~시죠)
- 과도한 리스트 나열
- 딱딱한 전문용어만 사용
- 이모지 남발 (블로그는 절제)
"""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """설정 인스턴스 반환 (lazy initialization)"""
    return Settings()


# 글로벌 설정 인스턴스
settings = get_settings()
