import logging
from abc import ABC, abstractmethod
from typing import Any
from openai import OpenAI
from emotion_aware_assistant.core.context import ConversationContext
from emotion_aware_assistant.utils.rate_limiter import rate_limited

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    """Base class for all action handlers"""
    
    @abstractmethod
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        """Execute the handler logic and return updated context"""
        pass
    
    def _get_full_input(self, context: ConversationContext) -> str:
        """Combine history with current input"""
        return "\n".join(context.history + [context.user_input])
    
    @rate_limited
    def _call_llm(self, openai_client: OpenAI, system_prompt: str, 
                  user_message: str, model: str = "gpt-4o-mini", 
                  max_tokens: int = 300) -> str:
        """Standardized LLM call"""
        try:
            response = openai_client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.info(f"LLM call error: {e}")
            return "I'm having trouble processing that right now. Could you try rephrasing?"