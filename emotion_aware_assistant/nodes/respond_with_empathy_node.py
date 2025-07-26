from emotion_aware_assistant.services.assistant import respond_with_empathy
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state 

def respond_with_empathy_node(state: GraphState) -> GraphState:
    """
    Process user input with empathy and return updated state with error handling.
    """
    try:
        state = ensure_graph_state(state)  
        print("💥 DEBUG: State type:", type(state))
        print("💥 DEBUG: State content:", state)
        print("🔍 node:", __name__)

        user_input = (state.input or "").strip()
        history = list(state.history or [])  # Create a copy
        emotion_history = list(state.emotion_history or [])  # Create a copy

        # Validate that we have input to process
        if not user_input:
            print("⚠️ No user input to process")
            return GraphState(
                **state.dict(),
                final_response="I didn't receive any input to process. Could you please share what's on your mind?"
            )

        # Get empathetic response
        result = respond_with_empathy(user_input)
        print(f"🔍 Empathy result: emotion={result.emotion}, response_length={len(result.response or '')}")

        # Update emotion history if emotion detected
        if result.emotion:
            emotion_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "emotion": result.emotion
            })

        # Update conversation history
        history.append(f"User: {user_input}")
        if result.response:
            history.append(f"Assistant: {result.response}")

        # Build new state dictionary first for debugging
        new_state_dict = {
            **state.dict(),
            'emotion': result.emotion,
            'final_response': result.response,
            'goal': result.goal,
            'suggested_action': result.suggested_action,
            'response_before_tool': result.response,
            'emotion_history': emotion_history,
            'history': history,
            'tool_result': None
        }
        
        print(f"🔍 New state dict keys: {list(new_state_dict.keys())}")
        
        # Create GraphState
        new_state = GraphState(**new_state_dict)

        print("✅ RETURNING TYPE:", type(new_state))
        print("✅ Successfully created GraphState")

        return new_state

    except Exception as e:
        print(f"❌ Error in respond_with_empathy_node: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a safe fallback state
        fallback_state = GraphState(
            **state.dict(),
            final_response=f"I encountered an error processing your message: {str(e)}",
            tool_result=None
        )
        return fallback_state
