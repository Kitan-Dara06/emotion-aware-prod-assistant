from emotion_aware_assistant.utils.helper import Reminder
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state
def Reminder_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    print("🔍 node:", __name__)

    history = state.history[-4:]  # ✅ access with dot notation
    full_input = "\n".join(history + [state.input])  # ✅

    reminder_result = Reminder(full_input)

    if "error" in reminder_result:
        return GraphState(
            **state.dict(),
            tool_result=f"⚠️ Could not extract reminder: {reminder_result['error']}",
            history=history + [state.input]
        )

    reminder = reminder_result['reminder']
    reminder_time = reminder_result['time']
    tool_result = f"🔔 Reminder set: {reminder} at {reminder_time}"
    print(tool_result)

    updated_reminders = state.reminder + [
        {"reminder": reminder, "time": reminder_time}
    ]

    return GraphState(
        **state.dict(),
        reminder=updated_reminders,
        tool_result=tool_result,
        history=history + [state.input]
    )
