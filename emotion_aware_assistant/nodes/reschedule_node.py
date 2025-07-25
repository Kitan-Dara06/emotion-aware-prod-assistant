# class RescheduleEventInput(BaseModel):
#   event :str
#   new_time : str
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.services.calendar import update_calendar_event
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state

def rescheduleEvent(full_input: str):
  # structured_result = llm.with_structured_output(schema=RescheduleEventInput)
  prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a tool for extracting reschedule instructions.

Only return a valid JSON with exactly two fields:
- "event": the original event name
- "new_time": the updated time

Example:
{{
  "event": "team meeting",
  "new_time": "Monday at 3pm"
}}

No extra text. No explanation. Just valid JSON.
"""),

        ("human", "{joined_input}")
    ])
  chain = prompt |  llm
  raw_output =   chain.invoke({"joined_input": full_input})
  try:
        match = re.search(r"\{.*?\}", raw_output.content, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found.")
        return json.loads(match.group())
  except Exception as e:
        return {"error": str(e), "raw_output": raw_output.content[:1000]}



def Reschedule_node(state: GraphState) -> GraphState:
  
    history = state.history[-4:]
    state = ensure_graph_state(state)
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    full_input = "\n".join(history + [state.input])

    reschedule_result = rescheduleEvent(full_input)

    if "error" in reschedule_result:
        return GraphState(
            **state.dict(),
            tool_result=f"⚠️ Could not extract reschedule info: {reschedule_result['error']}",
            history=history + [state.input]
        )

    reschedule_event = reschedule_result['event']
    reschedule_time = reschedule_result['new_time']
    tool_result = update_calendar_event(reschedule_event, reschedule_time)

    updated_event = state.schedule_event + [
        {"event": reschedule_event, "time": reschedule_time}
    ]

    return GraphState(
        **state.dict(),
        reschedule_event=updated_event,
        tool_result=tool_result,
        history=history + [state.input]
    )

