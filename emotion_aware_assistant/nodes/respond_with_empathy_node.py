from services.assistant import respond_with_empathy
from utils.types import GraphState
from gloabal_import import *


def respond_with_empathy_node(state: GraphState) -> GraphState:
    user_input = state.get("input", "").strip()
    history = state.get("history", [])
    emotion_history = state.get("emotion_history", [])

  
    result = respond_with_empathy(user_input)
  

    
    emotion = result.get("emotion")
    if emotion:
        emotion_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "emotion": emotion
        })

    
    if isinstance(user_input, str):
      history.append(f"User: {user_input}")
      history.append(f"Assistant: {result.get('response', '')}")


    return {
        **state,
        "emotion": result.get("emotion"),
        "final_response": result.get("response"),
        "goal": result.get("goal"),
        "suggested_action": result.get("suggested_action"),
        "response_before_tool": result.get("response"),
        "emotion_history": emotion_history,
        "history": history,
        "user_input": user_input,
        "awaiting_user_confirmation": state.get("awaiting_user_confirmation", False),
        "post_overwhelm": state.get("post_overwhelm", False),
    }
