from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.services.calendar import create_event
import re, json
from langchain_core.prompts import ChatPromptTemplate
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state


def scheduleEvent(full_input: str):
    Schedule_prompt = ChatPromptTemplate.from_messages([
        ("system", """
Only return a valid JSON with two fields:

- `event`: what the user wants to do
- `time`: when they want to do it

Example:
{{
  "event": "visit the market",
  "time": "5:30pm Thursday"
}}
DO NOT add any explanation or extra text.
"""),
        ("human", "{joined_input}")
    ])

    Schedule_chain = Schedule_prompt | llm
    raw_output = Schedule_chain.invoke({"joined_input": full_input})
    print("🧠 Raw LLM Output:", raw_output.content)

    try:
        match = re.search(r"\{.*?\}", raw_output.content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found.")
        parsed = json.loads(match.group())
        if "time" not in parsed or not parsed["time"]:
            return {
                "error": "Can you be more specific about when?",
                "raw_output": raw_output.content[:1000]
            }
        return parsed
    except Exception as e:
        return {
            "error": str(e),
            "raw_output": raw_output.content[:1000]
        }

def Schedule_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    history = state.history[-4:]
    full_input = "\n".join(history + [state.input])
    schedule_result = scheduleEvent(full_input)
    print("📦 scheduleEvent returned:", schedule_result)

    if "error" in schedule_result:
        return GraphState(
            **state.dict(),
            tool_result="Sorry, I couldn't understand what you want to schedule.",
            history=history + [state.input]
        )

    schedule_event = schedule_result.get('event', 'an event')
    schedule_time = schedule_result.get('time', 'sometime')

    tool_result = create_event(schedule_event, schedule_time)

    updated_events = state.schedule_event + [
        {"event": schedule_event, "time": schedule_time}
    ]

    return GraphState(
        **state.dict(),
        schedule_event=updated_events,
        tool_result=tool_result,
        history=history + [state.input]
    )
