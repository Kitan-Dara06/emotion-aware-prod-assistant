from emotion_aware_assistant.utils.helper import Reminder
from emotion_aware_assistant.utils.types import GraphState

def Reminder_node(state: GraphState) -> GraphState:
    history = state.get("history", [])[-4:]
    full_input = "\n".join(history + [state["input"]])
    reminder_result = Reminder(full_input)

    if "error" in reminder_result:
        return {
            **state,

          "tool_result": f"⚠️ Could not extract reminder: {reminder_result['error']}",
            "history": history + [state["input"]]
        }

    reminder = reminder_result['reminder']
    reminder_time = reminder_result['time']
    tool_result = f"🔔 Reminder set: {reminder} at {reminder_time}"
    print(tool_result)
    updated_reminders = state.get("reminder", []) + [
        {"reminder": reminder, "time": reminder_time}
    ]

    return {
        **state,
        'reminder': updated_reminders,
        'tool_result': tool_result,
        'history': history + [state["input"]]
    }
