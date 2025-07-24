from emotion_aware_assistant.nodes import *
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import*
from dotenv import load_dotenv
load_dotenv()

work_state = StateGraph(GraphState)


def fallback_node(state: GraphState) -> GraphState:
    return {
        **state,
        "final_response": "Hmm... I wasn't sure how to help with that. Could you rephrase?",
        "tool_result": None
    }







# work_state.add_node("welcome_node", welcome_node)
work_state.add_node('respond_with_empathy', respond_with_empathy_node)
work_state.add_node('reminder_node', Reminder_node)
work_state.add_node("overwhelm_node", overwhelm_node)
work_state.add_node("post_overwhelm_router_node", post_overwhelm_router_node)
work_state.add_node("prioritize_tasks_node", prioritize_tasks_node)
work_state.add_node('schedule_node', Schedule_node)
work_state.add_node('vent_node', vent_node)
work_state.add_node('talk_only_node', talk_only_node)
# work_state.add_node("prioritize_tasks", prioritize_tasks_node)

work_state.add_node('fetch_info_node', fetch_info_node)
work_state.add_node('continue_conversation_node',continue_conversation_node)
work_state.add_node('answer_question_node',answer_question_node)
work_state.add_node('give_advice_node',give_advice_node)
work_state.add_node('do_nothing_node',do_nothing_node)
work_state.add_node('summarize_input_node',summarize_input_node)
work_state.add_node('reschedule_node', Reschedule_node)
work_state.add_node("final_response_node", final_response_node)
# work_state.add_node("user_profile_node", user_profile_node)
work_state.add_node("fallback_node", fallback_node)

work_state.add_conditional_edges(
    "respond_with_empathy",
    lambda state: state["suggested_action"],
    {
        "overwhelm": "overwhelm_node",
        "set_reminder": "reminder_node",
        "schedule_event": "schedule_node",
        "reschedule_event": "reschedule_node",
        "answer_question" : 'answer_question_node',
        "summarize_input":'summarize_input_node',
        "vent":'vent_node',

        "do_nothing":'do_nothing_node',
        "give_advice":'give_advice_node',
        "fetch_info": "fetch_info_node",
        "continue_conversation":'continue_conversation_node',
        "fallback": "fallback_node"
    }

)

work_state.add_conditional_edges("post_overwhelm_router_node", post_overwhelm_router_node, {
    "reschedule_node": "reschedule_node",
    "prioritize_tasks_node": "prioritize_tasks_node",
    "talk_only_node": "talk_only_node",
    "final_response_node": "final_response_node"
})


# work_state.set_entry_point("user_profile_node")
work_state.set_entry_point("respond_with_empathy")
work_state.set_finish_point('final_response_node')

# work_state.add_edge("welcome_node", "user_profile_node")
# work_state.add_edge("user_profile_node", "respond_with_empathy")
# work_state.add_edge("welcome_node", "respond_with_empathy")
work_state.add_edge("overwhelm_node", "post_overwhelm_router_node")
work_state.add_edge("prioritize_tasks_node", "final_response_node")
work_state.add_edge('reminder_node', 'final_response_node')
work_state.add_edge('schedule_node', 'final_response_node')
work_state.add_edge("talk_only_node", "final_response_node")
work_state.add_edge( "answer_question_node", 'final_response_node')
work_state.add_edge( "summarize_input_node", 'final_response_node')
work_state.add_edge( "vent_node", 'final_response_node')
work_state.add_edge( "do_nothing_node", 'final_response_node')
work_state.add_edge( "give_advice_node", 'final_response_node')
work_state.add_edge( "fetch_info_node", 'final_response_node')
work_state.add_edge("overwhelm_node", "final_response_node")
work_state.add_edge( "continue_conversation_node", 'final_response_node')
work_state.add_edge('reschedule_node', 'final_response_node')
# work_state.set_entry_point("respond_with_empathy")

# Compile LangGraph
graph_app = work_state.compile()

from fastapi import FastAPI, Request
from pydantic import BaseModel

# FastAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://emotion-aware-assistant-frontend-ip0d88a4w.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Emotion-Aware Assistant is live 🚀"}



@app.post("/chat")
def run_graph(user_input: str):
    print("Incoming request:")
    print(user_input)

    try:
        initial_state = {
            "input": user_input.input,
            "user_profile": user_input.user_profile,
            "history": user_input.history,
            "emotion_history": user_input.emotion_history,
        }

        if not user_input.input.strip():
            return welcome_node(initial_state)  # Pass real state here

        result = graph_app.invoke(initial_state)
        return result

    except Exception as e:
        print("Graph Error:", e)
        return JSONResponse(
            status_code=500,
            content={"final_response": "Oops! Something went wrong on our side. Please try again."}
        )
