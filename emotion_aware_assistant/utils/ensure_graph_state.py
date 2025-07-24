def ensure_graph_state(state):
    return GraphState(**state) if isinstance(state, dict) else state
