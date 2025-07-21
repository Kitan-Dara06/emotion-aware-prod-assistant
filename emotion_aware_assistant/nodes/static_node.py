from utils.types import GraphState
from gloabal_import import *
from services.llm_model import llm

def user_profile_node(state: GraphState) -> GraphState:
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

    response = (prompt | llm).invoke({"input": state["input"]})
    user_profile = response.content.strip()

    return {
        **state,
        "user_profile": user_profile
    }
    
def welcome_node(state: GraphState) -> GraphState:
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

    return {
        **state,
        "final_response": welcome_message
    }
