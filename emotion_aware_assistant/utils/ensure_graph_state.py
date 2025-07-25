from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
def ensure_graph_state(state) -> GraphState:
    print("📌 ensure_graph_state called with:", type(state))
    
    if isinstance(state, dict):
        print("🔧 Coercing dict to GraphState")
        return GraphState(**state)
    elif isinstance(state, GraphState):
        print("✅ Already a GraphState")
        return state
    else:
        raise ValueError("Invalid state type: expected dict or GraphState")
