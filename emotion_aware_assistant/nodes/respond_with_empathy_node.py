from emotion_aware_assistant.services.assistant import respond_with_empathy
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.utils.ensure_state import ensure_graph_state 

def respond_with_empathy_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    user_input = (state.input or "").strip()
    history = state.history or []
    emotion_history = state.emotion_history or []

  
    result = respond_with_empathy(user_input)
  

    
    emotion = result.emotion
    if emotion:
        emotion_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "emotion": emotion
        })

    
    if isinstance(user_input, str):
      history.append(f"User: {user_input}")
      history.append(f"Assistant: {result.response or ''}")


    return {
          **state.dict(),  
    "emotion": result.emotion,
    "final_response": result.response,
    "goal": result.goal,
    "suggested_action": result.suggested_action,
    "response_before_tool": result.response,
    "emotion_history": emotion_history,
    "history": history,
    "user_input": user_input,
    "awaiting_user_confirmation": getattr(state, "awaiting_user_confirmation", False),
    "post_overwhelm": getattr(state, "post_overwhelm", False),
    }
