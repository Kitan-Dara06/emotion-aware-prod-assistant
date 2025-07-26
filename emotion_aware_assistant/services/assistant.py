
from emotion_aware_assistant.services.emotion import detect_emotion
from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.emotion import detect_emotion
from emotion_aware_assistant.services.prompts import strict_system_prompt
from emotion_aware_assistant.utils.helper import parse_json_output


llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, max_tokens=100, temperature=0.7)

def respond_with_empathy(text):
    print("🟡 [Step 1] User input:", text)
    emotion = detect_emotion(text)

    prompt_text = strict_system_prompt.format(emotion=emotion, text=text)
    print("🟡 [Step 2] Prompt Sent To LLM:\n", prompt_text)


    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt_text)
    ])

    llm_chain = prompt | llm

    try:
        raw_output = llm_chain.invoke({}, config={"max_tokens": 300})
        print("🟡 [Step 3] LLM Raw Output:", raw_output)
        result =parse_json_output(raw_output)
        print("🟡 [Step 4] Parsed JSON:", result)
        return result
        
    except ChunkedEncodingError:
        return {"error": "Connection interrupted."}




