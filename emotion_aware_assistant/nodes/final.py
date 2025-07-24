from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm

def final_response_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    tool_output = state.tool_result
    user_profile = state.user_profile or "You appreciate warmth and gentle encouragement."

    if tool_output:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""You are an emotionally intelligent assistant.

{user_profile}

The user's request has already been handled.

Here’s what happened: {tool_result}

Your job is to repeat this back to the user in a friendly, human tone.

If the tool result includes a link (like a calendar event), include it **as-is** in the response.

Do NOT write [insert calendar link here] — actually use the full link inside your message.
"""),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

        response = (prompt | llm).invoke({
            "input": state.input or "",
            "tool_result": tool_output,
            "user_profile": user_profile
        })

        print("🧠 Final LLM Output:", response.content)
        final_message = getattr(response, 'content', None) or getattr(response, 'text', None) or str(response)
        print("🗣️ FINAL RESPONSE STORED:", final_message)

        return {
            **state.dict(),
            "final_response": final_message
        }

    else:
        return {
            **state.dict(),
            "final_response": state.response_before_tool or "I'm here if you need anything else."
        }
