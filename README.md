# 🤖 AI 블로그 작가

> LangGraph v1.0 + Gemini 2.0 Flash 기반 Multi-Agent 블로그 자동 작성 시스템

AI가 자동으로 조사하고, 작성하고, 퇴고하는 전문적인 블로그 글 생성 시스템입니다. Human-in-the-Loop 방식으로 각 단계마다 사용자의 확인과 피드백을 받아 원하는 품질의 콘텐츠를 생성합니다.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-green.svg)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 주요 기능

- 🔍 **자동 조사**: Tavily Search API로 최신 정보 심층 조사
- ✍️ **AI 글쓰기**: Gemini 2.0 Flash로 전문적인 블로그 글 작성
- 🎨 **SEO 최적화**: 자동 퇴고 및 SEO 점수 분석 (가독성, 키워드 밀도, 구조)
- 💬 **질문 시스템**: AI가 부족한 정보를 자동으로 질문하고 사용자 답변 반영
- 👤 **Human-in-the-Loop**: 각 단계마다 사용자 승인 및 피드백 기능
- 💾 **마크다운 저장**: Frontmatter 포함 마크다운 파일 자동 생성
- 🌐 **웹 UI**: Streamlit 기반 직관적인 사용자 인터페이스
- 🔄 **워크플로우 저장**: SQLite 체크포인트로 진행상황 자동 저장

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/kimsol1134/ai_writer.git
cd ai_writer

# Python 가상 환경 생성 (Python 3.11+ 권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
# 또는 uv 사용 (더 빠름)
# pip install uv
# uv pip install -r requirements.txt
```

### 2. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일을 열어 아래 API 키들을 입력하세요:

#### 필수 API 키

1. **Google Gemini API** ([발급 방법](https://ai.google.dev/))
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

2. **Tavily Search API** ([발급 방법](https://tavily.com/))
   ```
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

#### 선택 사항

- **LangSmith** (디버깅/모니터링용, [발급 방법](https://smith.langchain.com/))
   ```
   LANGSMITH_API_KEY=your_langsmith_key_here
   LANGSMITH_TRACING=true
   ```

### 3. 실행

**Streamlit UI 실행**:
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📖 사용 방법

### 기본 워크플로우

1. **주제 입력**: 블로그 주제와 키워드 입력
2. **질문 응답** (필요시): AI가 추가 정보를 질문하면 답변
3. **조사 검토**: AI가 조사한 내용 확인 및 승인/거부
4. **초안 검토**: 작성된 초안 확인 및 수정 요청 가능
5. **최종 검토**: SEO 최적화된 최종본 확인
6. **다운로드**: 마크다운 파일 다운로드 또는 클립보드 복사

### 상세 사용법

#### 1단계: 주제 설정
```
주제: "소아 열성 경련 대처법"
키워드: "열성 경련, 대처법, 응급처치"
```

#### 2단계: AI 질문 응답 (자동)
AI가 글 작성에 필요한 정보를 질문합니다:
- "타겟 독자층은 누구인가요?"
- "어떤 관점에서 다루기를 원하시나요?"
- 등등...

#### 3단계: 조사 검토
- Tavily API로 수집한 최신 정보 확인
- 승인 시 → 다음 단계 진행
- 거부 시 → 재조사 요청 가능

#### 4단계: 초안 검토
- AI가 작성한 초안 확인
- 피드백 제공 가능 (예: "도입부를 더 감성적으로 수정해줘")
- 승인 시 → 퇴고 진행

#### 5단계: 최종본 확인
- SEO 최적화된 최종본 확인
- SEO 점수 확인 (가독성, 키워드 밀도, 구조)
- 다운로드 또는 클립보드 복사

## ✍️ 커스텀 작성 스타일 설정

이 시스템은 **당신만의 글쓰기 스타일**을 적용하여 블로그를 작성합니다.

### 기본 스타일 특징

현재 설정된 스타일:
- **톤**: 전문 지식을 스토리로 풀어내는 스타일
- **구조**: SUCCES 프레임워크 (도입부 Hook → 본론 Solution → 결론 Action)
- **문체**: 평어체 (~했다, ~다), 대화형 질문, 솔직한 표현
- **제목**: 질문형/숫자+구체성/감성형/전문성 강조 중 선택

### 스타일 확인하기

Streamlit UI 사이드바에서 "✍️ 내 작성 스타일 보기/편집"을 열어 현재 스타일을 확인할 수 있습니다.

### 스타일 수정하기

자신만의 스타일로 변경하고 싶다면:

1. **설정 파일 열기**:
   ```bash
   # 코드 에디터로 config.py 열기
   open blog_writer/config.py
   # 또는
   code blog_writer/config.py
   ```

2. **`writing_style` 필드 수정**:
   ```python
   # blog_writer/config.py (25번째 줄부터)

   writing_style: str = """
   **내 작성 스타일 DNA:**
   1. 여기에 원하는 스타일 설명
   2. 톤앤매너 정의
   3. 구조 설명

   **문체 원칙:**
   - 평어체/존댓말 선택
   - 이모지 사용 여부
   - 문장 길이 선호도

   **금지 사항:**
   - 피하고 싶은 표현
   - 사용하지 않을 톤
   """
   ```

3. **저장 후 재시작**:
   ```bash
   # Streamlit 재시작 (Ctrl+C 후)
   streamlit run app.py
   ```

### 스타일 예시

#### 예시 1: 전문적 스타일
```python
writing_style: str = """
- 데이터와 통계 중심
- 객관적이고 신뢰감 있는 톤
- 존댓말 사용 (~합니다, ~입니다)
- 이모지 최소화
"""
```

#### 예시 2: 친근한 스타일
```python
writing_style: str = """
- 친구와 대화하듯 편안한 톤
- 평어체 사용 (~했어요, ~해요)
- 공감 표현 많이 사용
- 이모지 적절히 활용
"""
```

#### 예시 3: 교육적 스타일
```python
writing_style: str = """
- 단계별 설명 중심
- "왜?"와 "어떻게?" 집중
- 예시와 비유 활용
- 명확한 구조 (정의→예시→요약)
"""
```

### 주의사항

- 스타일 변경 후 반드시 Streamlit을 재시작해야 적용됩니다
- 너무 복잡한 지시사항은 LLM이 제대로 따르지 못할 수 있습니다
- 명확하고 구체적인 지시를 2-3줄로 요약하는 것이 효과적입니다

## 🏗 아키텍처

### 워크플로우 다이어그램

```
입력 → [질문 생성] → [사용자 답변] → [조사] → [승인 1] → [작성] → [승인 2] → [퇴고] → [승인 3] → [저장]
          ↓                             ↑        ↓          ↑       ↓          ↑        ↓
       충분한 정보?                     거부    재조사       거부   재작성      거부    재퇴고
```

### 기술 스택

- **LangGraph 1.0**: 워크플로우 오케스트레이션
- **Google Gemini 2.0 Flash**: LLM 엔진
- **Tavily Search API**: 웹 검색 및 조사
- **Streamlit**: 웹 UI 프레임워크
- **SQLite**: 체크포인트 저장소
- **Pydantic**: 데이터 검증 및 타입 힌팅

### 주요 컴포넌트

1. **Agents** (`blog_writer/agents/`)
   - `research_agent.py`: 웹 검색 및 정보 수집
   - `writing_agent.py`: 블로그 초안 작성
   - `editing_agent.py`: 퇴고 및 SEO 최적화
   - `clarification_agent.py`: 사용자 질문 생성

2. **Tools** (`blog_writer/tools/`)
   - `tavily_search.py`: Tavily 검색 API 래퍼
   - `seo_analyzer.py`: SEO 점수 계산
   - `markdown_writer.py`: 마크다운 파일 생성

3. **State Management** (`blog_writer/state/`)
   - `blog_state.py`: 워크플로우 상태 관리 (TypedDict)

4. **Graph** (`blog_writer/graph.py`)
   - LangGraph StateGraph 정의
   - 노드 및 엣지 연결

## 📂 프로젝트 구조

```
ai_writer_new/
├── blog_writer/          # 메인 패키지
│   ├── agents/          # Agent 구현
│   ├── tools/           # 도구 구현
│   ├── state/           # 상태 정의
│   ├── nodes/           # 노드 함수
│   ├── graph.py         # LangGraph 워크플로우
│   └── config.py        # 설정 관리
├── output/              # 생성된 블로그 글
│   └── research/        # 조사 노트
├── checkpoints/         # SQLite 체크포인트
├── app.py               # Streamlit UI
├── requirements.txt     # 의존성 목록
└── README.md
```

## 🛠 개발 가이드

### 요구사항

- Python 3.11 이상
- API 키: Google Gemini, Tavily Search

### 테스트 실행

```bash
# 테스트 설치 (선택사항)
pip install pytest pytest-asyncio

# 모든 테스트 실행
pytest tests/

# 특정 테스트만 실행
pytest tests/test_graph.py
```

### 프로젝트 확장

#### 새로운 Agent 추가
```python
# blog_writer/agents/your_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from blog_writer.config import get_settings

def create_your_agent():
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=settings.temperature
    )
    # Agent 로직 구현
    return agent
```

#### 커스텀 Tool 추가
```python
# blog_writer/tools/your_tool.py
from langchain.tools import tool

@tool
def your_custom_tool(query: str) -> str:
    """Tool 설명"""
    # Tool 로직 구현
    return result
```

### 주요 설정 파일

- `blog_writer/config.py`: 모든 설정 관리 (모델, API, 경로 등)
- `.env`: 환경 변수 및 API 키
- `requirements.txt`: Python 의존성

### 디버깅

LangSmith를 사용하면 워크플로우를 시각화하고 디버깅할 수 있습니다:

1. `.env`에서 LangSmith 설정
   ```
   LANGSMITH_API_KEY=your_key
   LANGSMITH_TRACING=true
   ```

2. [LangSmith 대시보드](https://smith.langchain.com/)에서 실행 로그 확인

## 🐛 문제 해결

### 자주 발생하는 오류

#### 1. API 키 오류
```
Error: API key not found
```
**해결책**: `.env` 파일에 올바른 API 키가 설정되어 있는지 확인

#### 2. 모듈 import 오류
```
ModuleNotFoundError: No module named 'langgraph'
```
**해결책**:
```bash
pip install -r requirements.txt
```

#### 3. Streamlit 포트 충돌
```
Error: Address already in use
```
**해결책**:
```bash
streamlit run app.py --server.port 8502
```

## 🤝 기여하기

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 글

이 프로젝트는 다음 오픈소스 프로젝트들을 사용합니다:

- [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain - Multi-Agent 워크플로우
- [Google Gemini 2.0 Flash](https://ai.google.dev/) - LLM 엔진
- [Tavily Search API](https://tavily.com/) - 웹 검색
- [Streamlit](https://streamlit.io/) - 웹 UI 프레임워크

## 📧 연락처

질문이나 제안사항이 있으시면 [GitHub Issues](https://github.com/kimsol1134/ai_writer/issues)를 통해 연락주세요.

---

**작성일**: 2025-01-14
**버전**: 1.0.0
**작성자**: [@kimsol1134](https://github.com/kimsol1134)
