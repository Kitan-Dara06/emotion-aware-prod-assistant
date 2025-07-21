from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.services.calendar import get_calendar_service
from emotion_aware_assistant.services.calendar import fetch_upcoming_events
from emotion_aware_assistant.services.llm_model import llm

def overwhelm_node(state: GraphState) -> GraphState:
    service = get_calendar_service()
    upcoming_events = fetch_upcoming_events(service)

    tasks = []
    reminder = getattr(state, "reminder", None)

    if reminder:
        tasks.append(f"🔔 Reminder: {state['reminder']} at {state['reminder_time']}")

    tasks.extend(upcoming_events)
    joined_tasks = "\n".join(tasks) or "No upcoming tasks found."
    user_profile = state.get("user_profile", "You prefer warm, emotionally supportive responses.")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""
You're an emotionally aware assistant. The user is feeling overwhelmed.

The user values this support style: {user_profile}

You'll receive a list of upcoming tasks.

1. Summarize them gently using warm, human-like phrasing.
2. Acknowledge the emotional weight.
3. Offer to help — either by rescheduling or prioritizing.

Be validating, calm, and encouraging.
"""),
        HumanMessage(content=f"""
Here are the user's upcoming tasks:

{joined_tasks}
""")
    ])

    response = (prompt | llm).invoke({"joined_tasks": joined_tasks})

    return {
        **state,
        "awaiting_user_confirmation": True,
          "post_overwhelm": True,
        "tool_result": None,
        "final_response": response.content.strip()




    }

