import logging
from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state

logger = logging.getLogger(__name__)

def user_profile_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    print("🔍 node:", __name__)
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)
    print("🧠 Entered user_profile_node with:", state)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""
You are a personality profiler for an emotionally aware assistant.

Ask the user how they prefer responses — their ideal tone and style.

Examples:
- “Do you prefer quick, concise replies or deeper emotional reflections?”
- “Would you rather get straight to the point or talk through things gently?”

Be warm and curious.
"""),
        HumanMessage(content="{input}")
    ])

    response = (prompt | llm).invoke({"input": state.get("input", "")})
    user_profile = response.content.strip()

    return GraphState(
        **state.dict(),
        user_profile=user_profile
    )
    
def welcome_node(state: GraphState) -> GraphState:
    print("👋 Entered welcome_node with:", state)
    state = ensure_graph_state(state)
    print("💥 DEBUG: State type:", type(state))
    print("💥 DEBUG: State content:", state)

    user_input = state.get("input", "").strip()

    if not user_input:
        welcome_message = """
👋 Hey there! I’m your emotionally aware productivity assistant.

Here’s what I can help you with:
- 🧠 Understand how you're feeling and respond gently  
- 🔔 Set reminders for important tasks  
- 📅 Schedule or reschedule calendar events  
- 💬 Let you vent or talk things through  
- ✅ Help you prioritize when you're overwhelmed  
- 🧭 Give advice, answer questions, or just chat

Just tell me what’s on your mind, and I’ll take it from there.
"""
        return state.copy(update={"final_response": welcome_message})

    return state
