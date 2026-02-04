import logging
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *

logger = logging.getLogger(__name__)
def ensure_graph_state(state) -> GraphState:
    print("📌 ensure_graph_state called with:", type(state))
    
    if isinstance(state, dict):
        logger.info("🔧 Coercing dict to GraphState")
        return GraphState(**state)
    elif isinstance(state, GraphState):
        logger.info("Already a GraphState")
        return state
    else:
        raise ValueError("Invalid state type: expected dict or GraphState")
