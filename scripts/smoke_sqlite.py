from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.scenarios import load_scenarios
from langgraph_agent_lab.state import initial_state
import os

cp = build_checkpointer('sqlite','test_checkpoints.db')
print('checkpointer:', type(cp))
graph = build_graph(checkpointer=cp)
scenarios = load_scenarios('data/sample/scenarios.jsonl')
state = initial_state(scenarios[0])
res = graph.invoke(state, config={'configurable':{'thread_id':state['thread_id']}})
print('route:', res.get('route'))
print('db exists:', os.path.exists('test_checkpoints.db'))
