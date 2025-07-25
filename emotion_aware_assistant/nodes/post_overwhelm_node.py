from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from typing import Literal

def post_overwhelm_router_node(state: GraphState) -> Literal[
    "reschedule_node", 
    "prioritize_tasks_node", 
    "talk_only_node", 
    "final_response_node"
]:
    followup = (getattr(state, "input", "") or "").lower()

    if getattr(state, "awaiting_user_confirmation", False):
        if "reschedule" in followup or "later" in followup:
            return "reschedule_node"
        elif "prioritize" in followup or "first" in followup or "important" in followup:
            return "prioritize_tasks_node"
        else:
            return "talk_only_node"
    return "final_response_node"
