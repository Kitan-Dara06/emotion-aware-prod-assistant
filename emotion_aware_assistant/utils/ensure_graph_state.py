from emotion_aware_assistant.utils.types import GraphState
from gloabal_import import *
def ensure_graph_state(state):
    return GraphState(**state) if isinstance(state, dict) else state
