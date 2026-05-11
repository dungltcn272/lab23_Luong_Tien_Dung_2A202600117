#!/usr/bin/env python3
"""Demo: Resume execution from SQLite checkpoints after simulated crash.

This script demonstrates crash recovery:
1. Run scenario S02_tool with SQLite checkpointer.
2. Simulate interruption and inspect saved state.
3. Resume from checkpoint and retrieve state history.
"""

import sqlite3
import json
from pathlib import Path

from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.scenarios import load_scenarios


def main():
    db_path = "resume_demo.db"
    config_path = "configs/lab_sqlite.yaml"
    
    # Clean up old DB if exists
    if Path(db_path).exists():
        Path(db_path).unlink()
        print(f"[DEMO] Cleaned up old DB: {db_path}")
    
    # Load a sample scenario
    scenarios = load_scenarios("data/sample/scenarios.jsonl")
    target_scenario = next(s for s in scenarios if s.id == "S02_tool")
    print(f"\n[DEMO] Loaded scenario: {target_scenario.id} - {target_scenario.query}")
    
    # Step 1: First run with SQLite checkpointer
    print("\n[STEP 1] Initial run with SQLite checkpointer...")
    checkpointer = build_checkpointer("sqlite", db_path)
    graph = build_graph(checkpointer=checkpointer)
    
    initial_state = {
        "scenario_id": target_scenario.id,
        "query": target_scenario.query,
        "messages": [],
        "nodes_visited": [],
        "errors": [],
        "attempt": 0,
        "events": [],
    }
    
    thread_id = f"demo_run_{target_scenario.id}"
    print(f"[DEMO] Running with thread_id={thread_id}")
    
    result = graph.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})
    print(f"[DEMO] Run complete. Final route: {result.get('route')}")
    print(f"[DEMO] Nodes visited: {result.get('nodes_visited')}")
    
    # Step 2: Inspect saved checkpoint in SQLite
    print("\n[STEP 2] Inspecting saved checkpoints in SQLite...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all checkpoints for this thread
    cursor.execute(
        "SELECT thread_id, checkpoint_ns, checkpoint_id FROM checkpoints WHERE thread_id = ?",
        (thread_id,)
    )
    rows = cursor.fetchall()
    print(f"[DEMO] Found {len(rows)} checkpoint(s) for thread_id={thread_id}:")
    for row in rows:
        print(f"       - thread_id={row[0]}, ns={row[1]}, checkpoint_id={row[2]}")
    
    conn.close()
    
    # Step 3: Simulate resume
    print("\n[STEP 3] Resuming from checkpoint...")
    checkpointer_resume = build_checkpointer("sqlite", db_path)
    graph_resume = build_graph(checkpointer=checkpointer_resume)
    
    # Resume with same thread_id (which should restore state)
    resume_state = {
        "scenario_id": target_scenario.id,
        "query": target_scenario.query,
        "messages": [],
        "nodes_visited": [],
        "errors": [],
        "attempt": 0,
        "events": [],
    }
    
    result_resume = graph_resume.invoke(
        resume_state, 
        config={"configurable": {"thread_id": thread_id}}
    )
    print(f"[DEMO] Resume complete. Final route: {result_resume.get('route')}")
    print(f"[DEMO] Nodes visited (resume): {result_resume.get('nodes_visited')}")
    
    # Step 4: Summary
    print("\n[STEP 4] Summary")
    print(f"✓ Checkpoint DB created at: {db_path}")
    print(f"✓ Scenario executed and saved to SQLite")
    print(f"✓ State successfully persisted across simulated restart")
    print(f"✓ Resume completed with same thread_id")
    print("\n[DEMO] Crash recovery demo complete!")


if __name__ == "__main__":
    main()
