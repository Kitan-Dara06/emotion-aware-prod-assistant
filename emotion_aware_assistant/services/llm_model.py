from gloabal_import import *
from config import api_key
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=100,
    temperature=0.7
)