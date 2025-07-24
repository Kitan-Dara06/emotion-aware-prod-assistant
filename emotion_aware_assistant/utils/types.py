from emotion_aware_assistant.gloabal_import import *



class GraphState(BaseModel):
    input: str
    emotion: Optional[str] = None
    goal: Optional[str] = None
    suggested_action: Optional[str] = None
    response: Optional[str] = None

    reminder: List[Dict[str, str]] = []
    schedule_event: List[Dict[str, str]] = []
    reschedule_event: List[Dict[str, str]] = []

    tool_result: Optional[str] = None
    history: List[str] = []
    emotion_history: List[Dict[str, str]] = []
    user_profile: Optional[str] = None

