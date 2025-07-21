# class RescheduleEventInput(BaseModel):
#   event :str
#   new_time : str
from gloabal_import import *
from services.llm_model import llm
from utils.types import GraphState
from services.calendar import update_calendar_event

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

def Reschedule_node(state: GraphState)-> GraphState:
  history = state.get("history", [])[:4]
  full_input = "\n".join(history + [state["input"]])
  reschedule_result = rescheduleEvent(full_input)
  reschedule_event = reschedule_result['event']
  reschedule_time = reschedule_result['new_time']
  tool_result = update_calendar_event(reschedule_event, reschedule_time)
  updated_event = state.get('schedule_event', []) + [
      {'event': reschedule_event, 'time':reschedule_time}
  ]
  return{
       **state,
       'reschedule_event' :updated_event,
       'tool_result' :tool_result,
       "history": history + [state["input"]]

   }

