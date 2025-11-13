import pytest
from blog_writer.graph import create_blog_graph
from blog_writer.state import BlogState
from langgraph.checkpoint.memory import MemorySaver


def test_graph_creation():
    """그래프 생성 테스트"""
    checkpointer = MemorySaver()
    graph = create_blog_graph(checkpointer)

    assert graph is not None
    assert hasattr(graph, 'stream')
    assert hasattr(graph, 'invoke')


@pytest.mark.skip(reason="API 키 필요")
def test_full_workflow():
    """전체 워크플로우 테스트 (API 키 필요)"""
    checkpointer = MemorySaver()
    graph = create_blog_graph(checkpointer)

    initial_state = {
        "topic": "테스트 주제",
        "keywords": ["테스트"],
        "target_length": 500,
        "messages": [],
        "current_stage": "initialized"
    }

    config = {"configurable": {"thread_id": "test-1"}}

    # 첫 번째 실행 (조사까지)
    events = list(graph.stream(initial_state, config))

    assert len(events) > 0
