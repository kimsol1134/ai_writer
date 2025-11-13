import streamlit as st
import uuid
from datetime import datetime
from pathlib import Path

from blog_writer.graph import create_blog_graph
from blog_writer.config import settings

# 페이지 설정
st.set_page_config(
    page_title="AI 블로그 작가",
    page_icon="✍️",
    layout="wide"
)

# 세션 상태 초기화
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
if 'graph' not in st.session_state:
    st.session_state.graph = create_blog_graph()
if 'current_state' not in st.session_state:
    st.session_state.current_state = None
if 'workflow_started' not in st.session_state:
    st.session_state.workflow_started = False

# 타이틀
st.title("✍️ AI 블로그 작가")
st.markdown("LangGraph v1.0 + Gemini 2.0 Flash로 블로그 자동 작성")

# 사이드바 - 설정
with st.sidebar:
    st.header("⚙️ 설정")

    st.info(f"""
    **모델**: {settings.model_name}
    **검색**: Tavily API
    **저장 위치**: {settings.output_dir}
    """)

    if st.button("🔄 새 작업 시작"):
        st.session_state.thread_id = None
        st.session_state.current_state = None
        st.session_state.workflow_started = False
        st.rerun()

    st.divider()

    # 작성 스타일 편집 (선택적)
    with st.expander("✍️ 내 작성 스타일 보기/편집"):
        st.markdown("**현재 작성 스타일:**")
        st.text_area(
            "스타일 가이드",
            value=settings.writing_style,
            height=300,
            disabled=True,
            help="스타일을 수정하려면 blog_writer/config.py의 writing_style 필드를 편집하세요."
        )
        st.caption("💡 스타일 수정: `blog_writer/config.py` 파일의 `writing_style` 필드를 편집하세요.")

# 메인 영역
if not st.session_state.workflow_started:
    # 입력 폼
    st.header("1️⃣ 블로그 주제 입력")

    with st.form("blog_input_form"):
        topic = st.text_input(
            "블로그 주제",
            placeholder="예: AI가 의료 분야에 미치는 영향"
        )

        keywords_input = st.text_input(
            "키워드 (쉼표로 구분)",
            placeholder="예: 인공지능, 의료진단, 환자케어, 머신러닝"
        )

        target_length = st.slider(
            "목표 길이 (단어 수)",
            min_value=1000,
            max_value=5000,
            value=2000,
            step=100
        )

        submit = st.form_submit_button("🚀 블로그 작성 시작")

    if submit and topic:
        # 키워드 파싱
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]

        # 새 스레드 생성
        st.session_state.thread_id = str(uuid.uuid4())

        # 초기 상태
        initial_state = {
            "topic": topic,
            "keywords": keywords,
            "target_length": target_length,
            "messages": [],
            "current_stage": "initialized"
        }

        # 워크플로우 시작
        st.session_state.workflow_started = True

        config = {
            "configurable": {
                "thread_id": st.session_state.thread_id
            }
        }

        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 그래프 실행
            for i, event in enumerate(st.session_state.graph.stream(
                initial_state,
                config,
                stream_mode="updates"
            )):
                # 인터럽트 확인
                if "__interrupt__" in event:
                    st.session_state.current_state = st.session_state.graph.get_state(config)
                    st.rerun()
                    break

                # 진행 상황 업데이트
                node_name = list(event.keys())[0]
                if node_name == "research":
                    progress_bar.progress(20)
                    status_text.text("🔍 조사 중...")
                elif node_name == "write":
                    progress_bar.progress(50)
                    status_text.text("✍️ 작성 중...")
                elif node_name == "edit":
                    progress_bar.progress(80)
                    status_text.text("🎨 퇴고 중...")
                elif node_name == "save":
                    progress_bar.progress(100)
                    status_text.text("✅ 완료!")

            # 최종 상태 확인
            st.session_state.current_state = st.session_state.graph.get_state(config)
            st.rerun()

        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.session_state.workflow_started = False

else:
    # 워크플로우 진행 중 - 승인 및 질문 UI
    if st.session_state.current_state:
        state_values = st.session_state.current_state.values

        # 현재 단계 표시
        current_stage = state_values.get("current_stage", "unknown")

        st.header(f"📍 현재 단계: {current_stage}")

        # 인터럽트 데이터 확인
        if hasattr(st.session_state.current_state, 'tasks') and st.session_state.current_state.tasks:
            # 승인 또는 질문 대기 중
            interrupt_data = None
            for task in st.session_state.current_state.tasks:
                if hasattr(task, 'interrupts') and task.interrupts:
                    interrupt_data = task.interrupts[0].value
                    break

            if interrupt_data:
                interrupt_type = interrupt_data.get("type", "approval")  # 🆕 타입 구분
                stage = interrupt_data.get("stage", "알 수 없음")
                message = interrupt_data.get("message", "")

                # 🆕 Clarification 질문 폼
                if interrupt_type == "clarification":
                    st.subheader(f"📋 {stage.upper()} 단계 사전 질문")
                    st.info(message)

                    # 진행률 표시
                    progress = 0.33 if stage == "research" else 0.66 if stage == "writing" else 1.0
                    st.progress(progress)

                    questions = interrupt_data.get("questions", [])

                    with st.form(f"clarification_{stage}"):
                        answers = []

                        # 모든 질문을 한 화면에 표시
                        for i, q in enumerate(questions, 1):
                            st.markdown(f"### Q{i}. {q['text']}")
                            answer = st.text_area(
                                label=f"답변 {i}",
                                placeholder=q.get('placeholder', ''),
                                key=f"{stage}_q{i}",
                                label_visibility="collapsed",
                                height=100
                            )
                            answers.append(answer)

                        st.divider()

                        col1, col2 = st.columns([1, 4])

                        with col1:
                            skip = st.form_submit_button("⏭️ 건너뛰기", type="secondary")

                        with col2:
                            submit = st.form_submit_button("✅ 답변 제출", type="primary")

                        if skip:
                            config = {
                                "configurable": {
                                    "thread_id": st.session_state.thread_id
                                }
                            }

                            from langgraph.types import Command

                            for event in st.session_state.graph.stream(
                                Command(resume={"skipped": True, "answers": []}),
                                config,
                                stream_mode="updates"
                            ):
                                if "__interrupt__" in event:
                                    break

                            st.session_state.current_state = st.session_state.graph.get_state(config)
                            st.rerun()

                        if submit:
                            config = {
                                "configurable": {
                                    "thread_id": st.session_state.thread_id
                                }
                            }

                            from langgraph.types import Command

                            # 빈 답변 포함하여 제출 (사용자가 선택적으로 답변 가능)
                            filtered_answers = [a.strip() for a in answers]

                            for event in st.session_state.graph.stream(
                                Command(resume={"skipped": False, "answers": filtered_answers}),
                                config,
                                stream_mode="updates"
                            ):
                                if "__interrupt__" in event:
                                    break

                            st.session_state.current_state = st.session_state.graph.get_state(config)
                            st.rerun()

                # Approval 폼
                elif interrupt_type == "approval":
                    st.info(f"**{stage}** 단계 검토가 필요합니다.")

                    # 콘텐츠 표시
                    content = interrupt_data.get("content", "")

                    # 단계별 내용 표시
                    if stage == "research" or stage == "조사":
                        st.subheader("📚 조사 결과")
                        sources = interrupt_data.get("sources", [])

                        st.markdown(content)

                        with st.expander("📖 참고 자료"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"{i}. {source}")

                    elif stage == "writing" or stage == "초안":
                        st.subheader("✍️ 작성된 초안")

                        outline = interrupt_data.get("outline", "")
                        if outline:
                            with st.expander("📝 개요"):
                                st.markdown(outline)

                        st.markdown(content)

                    elif stage == "editing" or stage == "최종":
                        st.subheader("🎨 최종 버전")

                        seo_score = interrupt_data.get("seo_score", 0)
                        st.metric("SEO 점수", f"{seo_score}/100")

                        st.markdown(content)

                    # 승인/거부 버튼
                    st.markdown("---")
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("✅ 승인하고 다음 단계로", key="approve", type="primary"):
                            # 승인 응답
                            config = {
                                "configurable": {
                                    "thread_id": st.session_state.thread_id
                                }
                            }

                            from langgraph.types import Command

                            # 그래프 재개
                            for event in st.session_state.graph.stream(
                                Command(resume={"approved": True, "feedback": ""}),
                                config,
                                stream_mode="updates"
                            ):
                                if "__interrupt__" in event:
                                    break

                            st.session_state.current_state = st.session_state.graph.get_state(config)
                            st.rerun()

                    with col2:
                        if st.button("❌ 수정 요청", key="reject"):
                            feedback = st.text_area("수정 요청 사항", key="feedback_input")

                            if st.button("수정 요청 제출", key="submit_feedback"):
                                config = {
                                    "configurable": {
                                        "thread_id": st.session_state.thread_id
                                    }
                                }

                                from langgraph.types import Command

                                # 그래프 재개 (거부)
                                for event in st.session_state.graph.stream(
                                    Command(resume={"approved": False, "feedback": feedback}),
                                    config,
                                    stream_mode="updates"
                                ):
                                    if "__interrupt__" in event:
                                        break

                                st.session_state.current_state = st.session_state.graph.get_state(config)
                                st.rerun()

        # 완료 확인
        if state_values.get("current_stage") == "complete":
            st.success("🎉 블로그 작성이 완료되었습니다!")

            output_file = state_values.get("output_file", "")
            if output_file:
                st.info(f"📁 저장 위치: `{output_file}`")

                # 다운로드 버튼
                if Path(output_file).exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    st.download_button(
                        label="📥 마크다운 파일 다운로드",
                        data=content,
                        file_name=Path(output_file).name,
                        mime="text/markdown"
                    )

            if st.button("🔄 새 블로그 작성"):
                st.session_state.thread_id = None
                st.session_state.current_state = None
                st.session_state.workflow_started = False
                st.rerun()
