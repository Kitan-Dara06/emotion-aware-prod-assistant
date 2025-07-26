from emotion_aware_assistant.utils.types import GraphState
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm
from emotion_aware_assistant.utils.ensure_graph_state import ensure_graph_state  
from emotion_aware_assistant.utils.trim import cleanly_truncate
from emotion_aware_assistant.utils.trim import trim_to_last_full_sentence

def vent_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)  
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)
    user_profile = state.user_profile or "You prefer warm, human responses."

    full_input = "\n".join( [h for h in state.history or [] if isinstance(h, str)] + [state.input or ""] )
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("""
          You're a compassionate and emotionally intelligent assistant.
          {user_profile}
          You're a safe space for users to express their emotions.
          The user is venting. Don’t try to fix or explain anything. Just reflect their feelings and validate them.
         Be gentle, nonjudgmental, and empathetic. Let them feel seen.
        The user just wants to vent and express their emotions.
       Let them feel heard. Don't interrupt or problem-solve.
         Validate what they’re saying and gently offer support if appropriate.   """),
        HumanMessagePromptTemplate.from_template("{joined_input}")])

    response = (prompt | llm).invoke({
        "joined_input": full_input,
        "user_profile": user_profile
    })
    final_message = response.content
    updated_state = state.dict()
    updated_state["final_response"] = final_message
    updated_state["response"] = final_message
    updated_state["tool_result"] = None
    return GraphState(**updated_state)    




def answer_question_node(state : GraphState) -> GraphState:
  state = ensure_graph_state(state)
  print("🔍 node:", __name__)
  print("🔍 state type:", type(state))
  print("🔍 state content:", state)
  full_input = "\n".join( [h for h in state.history or [] if isinstance(h, str)] + [state.input or ""])  
  user_profile = state.user_profile or "You prefer warm, human responses."
  prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
      You are an emotionally aware assistant helping answer user questions thoughtfully and clearly.

         Context about the user:
    {user_profile}

          Here is the question the user just asked:
    \"\"\"{input}\"\"\"

         Use a supportive tone and give a clear, helpful response.
       Avoid hallucinating or changing the topic.
          """),
            HumanMessagePromptTemplate.from_template("{joined_input}")
])

  response = (prompt | llm).invoke({
    "input" : state.input,
    "user_profile" : state.user_profile or "",
    "joined_input": full_input
})

  final_summary = cleanly_truncate(response.content)
  final_summary = trim_to_last_full_sentence(final_summary, word_limit=150)
  updated_state = state.dict()
  updated_state["final_response"] = final_summary
  updated_state["response"] = final_summary
  updated_state["tool_result"] = None
    return GraphState(**updated_state)  

  
def do_nothing_node(state: GraphState) -> GraphState:
    """Handles casual or non-actionable input in a friendly, human-like way."""
    
    state = ensure_graph_state(state)
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)

    full_input = "\n".join(
        [h for h in state.history or [] if isinstance(h, str)] + [state.input or ""]
    )


    user_profile = state.user_profile or "You prefer warm, human responses."

    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """The user just said something casual or friendly, like a joke, meme, or light comment.
{user_profile}
Respond in a relaxed, human tone. Acknowledge their message, and if it feels natural, ask a playful follow-up or express curiosity.
No advice or emotion processing here — just chill, friendly chat like you'd have with someone close."""
        ),
        HumanMessagePromptTemplate.from_template("{joined_input}")
    ])

    try:
       
        chain: Runnable = prompt | llm
        result = chain.invoke({
            "joined_input": full_input,
            "user_profile": user_profile
        })

        final_message = result.content

    except Exception as e:
        logger.exception("⚠️ Error in do_nothing_node LLM call.")
        final_message = "Hehe, got it 😅 Just here if you need anything."

    # Safe state mutation
    updated_state = state.dict()
    updated_state["final_response"] = final_message
    updated_state["response"] = final_message
    updated_state["tool_result"] = None

    return GraphState(**updated_state)    

def give_advice_node(state : GraphState) -> GraphState:
  state = ensure_graph_state(state)  
  print("🔍 node:", __name__)
  print("🔍 state type:", type(state))
  print("🔍 state content:", state)
  full_input = "\n".join(  [h for h in state.history or [] if isinstance(h, str)] + [state.input or ""])
  
  prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate.from_template("""The user is asking for advice on what to do in their situation.

Give a thoughtful, emotionally aware answer. It’s okay to offer some light direction — just don’t be forceful.

Gently guide them by highlighting trade-offs or options. Encourage reflection while offering support.
"""),
      HumanMessagePromptTemplate.from_template("{joined_input}")

  ])

  response = (prompt |llm ).invoke({"joined_input": full_input},)
  final_response = response.content
  updated_state = state.dict()
  updated_state['final_response'] = final_response
  updated_state['response'] = final_response
  updated_state['tool_result'] = None
  return GraphState(**updated_state)


  



def continue_conversation_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)

    full_input = "\n".join([h for h in state.history or [] if isinstance(h, str)] + [state.input or ""])
    user_profile = state.user_profile or "You prefer warm, human responses."
    
    try:
        emotion = state.emotion or ""
        print(f"🔍 Emotion accessed successfully: '{emotion}'")
    except AttributeError as e:
        print(f"❌ Error accessing emotion: {e}")
        print(f"🔍 State attributes: {dir(state)}")
        emotion = ""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """You are a caring assistant continuing a heartfelt conversation.

The user's current emotion is: {emotion}
Your job is to keep the conversation flowing naturally with empathy.

Be warm, emotionally aware, and ask a gentle follow-up.
Do not give advice or solutions here  just invite them to share more."""
        ),
        HumanMessagePromptTemplate.from_template("{joined_input}")
    ])

    response = (prompt | llm).invoke({
        "emotion": emotion,
        "joined_input": full_input,
        "user_profile": user_profile,
    })
    final_response = response.content
    updated_state = state.dict()
    updated_state["final_response"] =final_response
    updated_state["response"] = final_response
    updated_state['tool_result'] = None
    return GraphState(**updated_state)

   
  
def fetch_info_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)  
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)
    user_input = (state.input or "").strip()
    history = state.history or []
    user_profile = state.user_profile or "You prefer warm, human responses."

    # Validate input
    if not user_input:
        return GraphState (
            **state.dict(),
            tool_result = None,
            final_response="It seems like your message wasn’t complete. Could you tell me more about what you need help with?",
            
        )

    
    full_input = "\n".join(history + [user_input])

   
    info_llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        api_key=api_key,
        temperature=0.5,
        max_tokens=300
    )

    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("""
You’re an assistant who provides helpful, emotionally aware information.

The user wants facts, suggestions, or resources.
Be accurate and human. If it’s a list or recommendation, briefly explain how it helps.

User profile: {user_profile}
"""),
        HumanMessagePromptTemplate.from_template("{joined_input}")
    ])

    chain = prompt | info_llm

   
    try:
        response = chain.invoke({"joined_input": full_input,
                                "user_profile": user_profile})
        final_response = response.content.strip()
        clean_output = trim_to_last_full_sentence(final_response, word_limit=150)
        updated_state = state.dict()
        updated_state["final_response"] =clean_output
        updated_state["response"] = clean_output
        updated_state['tool_result'] = None
        return GraphState(**updated_state)
    except Exception as e:
        final_response = f"⚠️ Error during info fetch: {str(e)}"
        updated_state = state.dict()
        updated_state["final_response"] =final_response
        updated_state["response"] = final_response
        updated_state['tool_result'] = None
        return GraphState(**updated_state)
    
    
def summarize_input_node(state: GraphState) -> GraphState:
    state = ensure_graph_state(state)  
    print("🔍 node:", __name__)
    print("🔍 state type:", type(state))
    print("🔍 state content:", state)
    user_input = state.input or ""

    if len(user_input.split()) > 500:
        return GraphState(
            **state.dict(),
            tool_result = None,
            final_response= (
                "That’s quite a lot to process at once. "
                "Could you shorten it to under 500 words so I can better understand and help?"
            )
        )

    summarizer_llm = ChatOpenAI(
        model="gpt-4o",
        api_key=api_key,
        temperature=0.2,
        max_tokens=700
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("""
You help users process big thoughts clearly.

Summarize what the user shared into a short, focused overview.

Be clear and emotionally aware, but don’t reflect past chats or context.
"""),
        HumanMessagePromptTemplate.from_template("{input_text}")
    ])

    chain = prompt | summarizer_llm

    try:
        response = chain.invoke({"input_text": user_input}) 
        final_summary = response.content.strip()
        updated_state = state.dict()
        updated_state["final_response"] = final_summary 
        updated_state["response"] = final_summary 
        updated_state['tool_result'] = None
        return GraphState(**updated_state)
    except Exception as e:
        final_response = f"⚠️ Error during info fetch: {str(e)}"
        updated_state = state.dict()
        updated_state["final_response"] =final_response
        updated_state["response"] = final_response
        updated_state['tool_result'] = None
        return GraphState(**updated_state)
    
    
