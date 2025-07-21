from emotion_aware_assistant.gloabal_import import *

class GraphState(TypedDict):
    input: str
    emotion: Optional[str]
    goal: Optional[str]
    suggested_action: Optional[str]
    response: Optional[str]

    reminder: List[Dict[str, str]]
    schedule_event: List[Dict[str, str]]
    reschedule_event: List[Dict[str, str]]

    tool_result: Optional[str]
    history: List[str]
    emotion_history: List[Dict[str, str]]
    user_profile: Optional[str]
