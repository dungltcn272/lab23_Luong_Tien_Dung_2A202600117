from langgraph_agent_lab.nodes import classify_node, tool_node, retry_or_fallback_node
from langgraph_agent_lab.routing import route_after_retry
from langgraph_agent_lab.state import Route


def test_classify_risky_keywords():
    state = {"query": "Please refund and cancel the order"}
    out = classify_node(state)
    assert out["route"] == Route.RISKY.value


def test_classify_tool_keywords():
    state = {"query": "Can you check my order status?"}
    out = classify_node(state)
    assert out["route"] == Route.TOOL.value


def test_retry_exhaustion_routes_to_dead_letter():
    # simulate state where attempt equals max_attempts
    s = {"attempt": 3, "max_attempts": 3}
    assert route_after_retry(s) == "dead_letter"


def test_tool_transient_failure_then_success():
    s = {"route": Route.ERROR.value, "attempt": 0, "scenario_id": "T1"}
    out1 = tool_node(s)
    assert "ERROR" in out1["tool_results"][0]
    # increment attempt then call tool again
    s2 = {"route": Route.ERROR.value, "attempt": 2, "scenario_id": "T1"}
    out2 = tool_node(s2)
    assert "ERROR" not in out2["tool_results"][0]
