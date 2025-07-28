from emotion_aware_assistant.nodes import *
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import*
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state
from dotenv import load_dotenv
load_dotenv()

work_state = StateGraph(GraphState)
work_state.debug = True


def fallback_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)

    final_response = "Hmm... I wasn't sure how to help with that. Could you rephrase?"
    updated_state = state.dict()
    updated_state['final_response'] = final_response
    updated_state['response'] = final_response
    updated_state['tool_result'] = None
    return GraphState(**updated_state)
   


# Conditional edge router functions with proper error handling
def route_suggested_action(state: GraphState) -> str:
    state = ensure_graph_state(state)
    suggested_action = state.suggested_action
    print(f"🔍 Routing suggested_action: '{suggested_action}'")
    
    # Define valid actions
    valid_actions = {
        "overwhelm", "set_reminder", "schedule_event", "reschedule_event",
        "answer_question", "summarize_input", "vent", "do_nothing",
        "give_advice", "fetch_info", "continue_conversation"
    }
    
    if suggested_action in valid_actions:
        return suggested_action
    else:
        print(f"⚠️ Unknown suggested_action: '{suggested_action}', routing to fallback")
        return "fallback"



# Add nodes
work_state.add_node('respond_with_empathy', respond_with_empathy_node)
work_state.add_node('reminder_node', Reminder_node)
work_state.add_node("overwhelm_node", overwhelm_node)
work_state.add_node("post_overwhelm_router_node", post_overwhelm_router_node)
work_state.add_node("prioritize_tasks_node", prioritize_tasks_node)
work_state.add_node('schedule_node', Schedule_node)
work_state.add_node('vent_node', vent_node)
work_state.add_node('talk_only_node', talk_only_node)
work_state.add_node('fetch_info_node', fetch_info_node)
work_state.add_node('continue_conversation_node', continue_conversation_node)
work_state.add_node('answer_question_node', answer_question_node)
work_state.add_node('give_advice_node', give_advice_node)
work_state.add_node('do_nothing_node', do_nothing_node)
work_state.add_node('summarize_input_node', summarize_input_node)
work_state.add_node('reschedule_node', Reschedule_node)
work_state.add_node("final_response_node", final_response_node)
work_state.add_node("fallback_node", fallback_node)

# Fixed conditional edges - use proper router function
work_state.add_conditional_edges(
    "respond_with_empathy",
    route_suggested_action,  # ✅ Use proper router function
    {
        "overwhelm": "overwhelm_node",
        "set_reminder": "reminder_node",
        "schedule_event": "schedule_node",
        "reschedule_event": "reschedule_node",
        "answer_question": 'answer_question_node',
        "summarize_input": 'summarize_input_node',
        "vent": 'vent_node',
        "do_nothing": 'do_nothing_node',
        "give_advice": 'give_advice_node',
        "fetch_info": "fetch_info_node",
        "continue_conversation": 'continue_conversation_node',
        "fallback": "fallback_node"
    }
)

work_state.add_conditional_edges(
    "post_overwhelm_router_node", post_overwhelm_router_node,
    {
        "reschedule_node": "reschedule_node",
        "prioritize_tasks_node": "prioritize_tasks_node",
        "talk_only_node": "talk_only_node",
        "final_response_node": "final_response_node"
    }
)

# Set entry and finish points
work_state.set_entry_point("respond_with_empathy")
work_state.set_finish_point('final_response_node')

# Add edges
work_state.add_edge("overwhelm_node", "post_overwhelm_router_node")
work_state.add_edge("prioritize_tasks_node", "final_response_node")
work_state.add_edge('reminder_node', 'final_response_node')
work_state.add_edge('schedule_node', 'final_response_node')
work_state.add_edge("talk_only_node", "final_response_node")
work_state.add_edge("answer_question_node", 'final_response_node')
work_state.add_edge("summarize_input_node", 'final_response_node')
work_state.add_edge("vent_node", 'final_response_node')
work_state.add_edge("do_nothing_node", 'final_response_node')
work_state.add_edge("give_advice_node", 'final_response_node')
work_state.add_edge("fetch_info_node", 'final_response_node')
work_state.add_edge("overwhelm_node", "final_response_node")
work_state.add_edge("continue_conversation_node", 'final_response_node')
work_state.add_edge('reschedule_node', 'final_response_node')

# Compile LangGraph
graph_app = work_state.compile()

from fastapi import FastAPI, Request
from pydantic import BaseModel

# FastAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://emotion-aware-assistant-frontend-nr5tt29qd.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/chat")
def preflight_check():
    return {"message": "Preflight passed"}

@app.get("/")
def read_root():
    return {"message": "Emotion-Aware Assistant is live 🚀"}

app.include_router(google_auth.router)

@app.post("/chat")
def run_graph(state: GraphState = Body(...)):
    print("Incoming state:", state)
    print("Incoming state 2:", type(state))
    
    try:
        state = ensure_graph_state(state)
        print("🔍 node:", __name__)
        print("Processed state:", state)
        print("Processed state type:", type(state))
        
        result = graph_app.invoke(state)
        return result
    except Exception as e:
        print("Graph Error:", str(e))
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"final_response": "Oops! Something went wrong on our side. Please try again."}
        )
