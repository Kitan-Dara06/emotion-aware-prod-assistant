
from services.emotion import detect_emotion
from gloabal_import import *
from services.emotion import detect_emotion
from services.prompts import strict_system_prompt
from utils.helper import parse_json_output


llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, max_tokens=100, temperature=0.7)

def respond_with_empathy(text):
    emotion = detect_emotion(text)

    prompt_text = strict_system_prompt.format(emotion=emotion, text=text)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=prompt_text)
    ])

    llm_chain = prompt | llm

    try:
        raw_output = llm_chain.invoke({}, config={"max_tokens": 300})
        return parse_json_output(raw_output)
    except ChunkedEncodingError:
        return {"error": "Connection interrupted."}




