from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm

def final_response_node(state: GraphState) -> GraphState:
    tool_output = state.get("tool_result")
    user_profile = state.get("user_profile", "You appreciate warmth and gentle encouragement.")

    if tool_output:
        system_message = f"""
You are an emotionally intelligent assistant.
{user_profile}
The user's request has already been handled.

Here’s what happened: {state.get('tool_result')}

Your job is to repeat this back to the user in a friendly, human tone.

If the tool result includes a link (like a calendar event), include it **as-is** in the response.

Do NOT write [insert calendar link here] — actually use the full link inside your message.
""".strip()

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            HumanMessage(content="{input}")
        ])

        response = (prompt | llm).invoke({
    "input": state["input"],
    "tool_result": tool_output
})
        print("🧠 Final LLM Output:", response.content)
        final_message = getattr(response, 'content', None) or getattr(response, 'text', None) or str(response)
        print("🗣️ FINAL RESPONSE STORED:", final_message)


        return {
            **state,
            "final_response": response.content
        }

    else:
        return {
            **state,
            "final_response": state.get("response_before_tool", "I'm here if you need anything else.")
        }
