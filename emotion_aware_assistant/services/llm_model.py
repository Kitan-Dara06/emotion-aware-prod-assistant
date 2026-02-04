# DEPRECATED: Old LangChain LLM initialization
# New implementation uses OpenAI client directly in handlers

import os
from openai import OpenAI
from emotion_aware_assistant.config import api_key

# For backward compatibility with old code
llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or api_key)
