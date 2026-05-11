#!/usr/bin/env python3
"""Export LangGraph graph as Mermaid diagram."""

from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.state import Route


def generate_mermaid_diagram() -> str:
    """Generate Mermaid diagram of the graph architecture."""
    
    diagram = """graph TD
    START[START] --> INTAKE[intake]
    INTAKE --> CLASSIFY{classify_node}
    
    CLASSIFY -->|route=simple| SIMPLE[simple_node]
    CLASSIFY -->|route=tool| TOOL[tool_node]
    CLASSIFY -->|route=missing_info| CLARIFY[clarify_node]
    CLASSIFY -->|route=risky| RISKY[risky_action_node]
    CLASSIFY -->|route=error| ERROR[error_node]
    
    SIMPLE --> EVALUATE[evaluate_node]
    TOOL --> EVALUATE
    CLARIFY --> EVALUATE
    RISKY --> APPROVAL[approval_node]
    ERROR --> EVALUATE
    
    APPROVAL --> EVALUATE
    
    EVALUATE -->|success| FINALIZE[finalize_node]
    EVALUATE -->|needs_retry| RETRY{route_after_retry<br/>attempt < max_attempts?}
    
    RETRY -->|retry| TOOL
    RETRY -->|dead_letter| DEADLETTER[dead_letter_node]
    
    DEADLETTER --> FINALIZE
    FINALIZE --> END[END]
    
    style START fill:#90EE90
    style END fill:#FFB6C6
    style CLASSIFY fill:#87CEEB
    style EVALUATE fill:#87CEEB
    style RETRY fill:#FFD700
    style APPROVAL fill:#DDA0DD
    style DEADLETTER fill:#FF6B6B"""
    
    return diagram


def main():
    diagram = generate_mermaid_diagram()
    output_file = "outputs/graph_diagram.mmd"
    
    with open(output_file, "w") as f:
        f.write(diagram)
    
    print(f"[EXPORT] Mermaid diagram exported to: {output_file}")
    print("[EXPORT] Diagram content:")
    print(diagram)


if __name__ == "__main__":
    main()
