def respond_with_empathy_node(state: GraphState) -> GraphState:

    state = ensure_graph_state(state)  
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    print("🔍 node:", __name__)

    user_input = (state.input or "").strip()
    history = state.history or []
    emotion_history = state.emotion_history or []

    try:
        result = respond_with_empathy(user_input)
        print(f"🔍 Result type: {type(result)}")
        
        # Handle dictionary result (which is what you're getting)
        if isinstance(result, dict):
            emotion = result.get('emotion')
            response = result.get('response')
            goal = result.get('goal')
            suggested_action = result.get('suggested_action')
        else:
            # Handle object result (just in case)
            emotion = getattr(result, 'emotion', None)
            response = getattr(result, 'response', None)
            goal = getattr(result, 'goal', None)
            suggested_action = getattr(result, 'suggested_action', None)

        print(f"🔍 Parsed - emotion: {emotion}, action: {suggested_action}")

        # Update emotion history
        if emotion:
            emotion_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "emotion": emotion
            })

        # Update conversation history
        if user_input:
            history.append(f"User: {user_input}")
            history.append(f"Assistant: {response or ''}")

        # Create new state using existing state as base
        new_state_data = state.dict()
        new_state_data.update({
            'emotion': emotion,
            'final_response': response,
            'goal': goal,
            'suggested_action': suggested_action,
            'response_before_tool': response,
            'emotion_history': emotion_history,
            'history': history,
            'tool_result': None
        })

        new_state = GraphState(**new_state_data)
        print("✅ RETURNING TYPE:", type(new_state))
        return new_state

    except Exception as e:
        print(f"❌ Error: {e}")
        # Safe fallback
        fallback_data = state.dict()
        fallback_data.update({
            'final_response': "I'm having trouble right now. Could you try rephrasing that?",
            'tool_result': None,
            'suggested_action': 'fallback'
        })
        return GraphState(**fallback_data)
