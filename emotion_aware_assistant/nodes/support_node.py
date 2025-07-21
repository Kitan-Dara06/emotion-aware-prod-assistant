from gloabal_import import *
from utils.types import GraphState
from services.llm_model import llm
from services.calendar import fetch_upcoming_events
from services.calendar import get_calendar_service
def talk_only_node(state: GraphState) -> GraphState:
    user_profile = state.get("user_profile", "You appreciate warmth and gentle encouragement.")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""
You're an emotionally supportive assistant. The user feels overwhelmed but just wants to talk.

Adapt your tone based on this profile: {user_profile}
- Listen actively.
- Offer gentle reassurance.
- No tools. No action suggestions.
"""),
        HumanMessage(content=state.get("user_input", "I'm overwhelmed."))
    ])

    response = (prompt | llm).invoke({})

    return {
        **state,
        "final_response": response.content.strip(),
        "tool_result": None,
        "suggested_action": "talk_only",
        "awaiting_user_confirmation": False
    }

def prioritize_tasks_node(state: GraphState) -> GraphState:
    tasks = []

    # 1. Local memory reminders
    reminder = getattr(state, "reminder", None)
    for r in reminder:
        tasks.append((r["time"], f"🔔 {r['text']} at {r['time']}"))

    # 2. Live Google Calendar events
    service = get_calendar_service()
    upcoming_events = fetch_upcoming_events(service)
    for event in upcoming_events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "No title")
        tasks.append((start, f"📅 {summary} at {start}"))

    # 3. Sort and format
    tasks.sort()
    prioritized = "\n".join(task[1] for task in tasks) or "No tasks to prioritize."

    # 4. LLM response (optional, like overwhelm node)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You're a kind, emotionally aware assistant. Help the user focus on their top priorities."),
        HumanMessage(content=f"Here are their tasks:\n{prioritized}")
    ])
    response = (prompt | llm).invoke({})

    return {
        **state,
        "tool_result": prioritized,
        "final_response": response.content.strip()
    }
