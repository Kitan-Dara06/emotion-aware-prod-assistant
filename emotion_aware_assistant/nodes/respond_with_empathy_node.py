from emotion_aware_assistant.services.assistant import respond_with_empathy
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state 

from emotion_aware_assistant.services.assistant import respond_with_empathy
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state 
from datetime import datetime

def respond_with_empathy_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)  
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    print("🔍 node:", __name__)

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

def respond_with_empathy_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)  
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    print("🔍 node:", __name__)

    user_input = (state.input or "").strip()
    history = state.history or []
    emotion_history = state.emotion_history or []

    result = respond_with_empathy(user_input)

    if result.emotion:
        emotion_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "emotion": result.emotion
        })

    if user_input:
        history.append(f"User: {user_input}")
        history.append(f"Assistant: {result.response or ''}")

    # ✅ Build and return a new GraphState
    new_state = GraphState(
        **state.dict(),  
        emotion=result.emotion,
        final_response=result.response,
        goal=result.goal,
        suggested_action=result.suggested_action,
        response_before_tool=result.response,
        emotion_history=emotion_history,
        history=history,
        # Only include the following if they exist in your GraphState model
        # awaiting_user_confirmation=getattr(state, "awaiting_user_confirmation", False),
        # post_overwhelm=getattr(state, "post_overwhelm", False),
    )

    print("✅ RETURNING TYPE:", type(new_state))
    print("✅ RETURNING CONTENT:", new_state)

    return new_state
        # 👇 Construct the new state
    # new_state = GraphState(
    #     **state.dict(),  
    #     emotion=result.emotion,
    #     final_response=result.response,
    #     goal=result.goal,
    #     suggested_action=result.suggested_action,
    #     response_before_tool=result.response,
    #     emotion_history=emotion_history,
    #     history=history,
    #     # 👇 REMOVE invalid keys like these if they're not in GraphState:
    #     # user_input=user_input,
    #     # awaiting_user_confirmation=...,
    #     # post_overwhelm=...,
    # )

    # # ✅ Confirm its type and content
    # print("✅ RETURNING TYPE:", type(new_state))
    # print("✅ RETURNING CONTENT:", new_state)

    # return new_state


    # return GraphState(
    #     **state.dict(),
    #     emotion=result.emotion,
    #     final_response=result.response,
    #     goal=result.goal,
    #     suggested_action=result.suggested_action,
    #     response_before_tool=result.response,
    #     emotion_history=emotion_history,
    #     history=history,
    #     # ONLY include these if they're defined in GraphState:
    #     # awaiting_user_confirmation=getattr(state, "awaiting_user_confirmation", False),
    #     # post_overwhelm=getattr(state, "post_overwhelm", False),
    # )
