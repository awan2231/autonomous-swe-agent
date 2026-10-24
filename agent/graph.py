from langgraph.graph import END, START, StateGraph

from agent.nodes import (
    apply_edits_node,
    fetch_issue_node,
    propose_fix_node,
    route_after_tests,
    run_tests_node,
)
from agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch_issue", fetch_issue_node)
    graph.add_node("run_tests", run_tests_node)
    graph.add_node("propose_fix", propose_fix_node)
    graph.add_node("apply_edits", apply_edits_node)

    graph.add_edge(START, "fetch_issue")
    graph.add_edge("fetch_issue", "run_tests")
    graph.add_conditional_edges(
        "run_tests",
        route_after_tests,
        {"done": END, "give_up": END, "retry": "propose_fix"},
    )
    graph.add_edge("propose_fix", "apply_edits")
    graph.add_edge("apply_edits", "run_tests")

    return graph.compile()