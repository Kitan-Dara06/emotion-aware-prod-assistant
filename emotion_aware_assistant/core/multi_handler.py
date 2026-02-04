import logging
from typing import List, Any
from openai import OpenAI
from .context import ConversationContext
from emotion_aware_assistant.handlers import get_handler

logger = logging.getLogger(__name__)

class MultiHandlerExecutor:
    """
    Execute multiple handlers in sequence and combine their responses naturally.
    
    Used when a single user message contains multiple intents, e.g.:
    - "I'm stressed and need to schedule a meeting" → [overwhelm, schedule_event]
    - "Help me prioritize tasks and set a reminder" → [prioritize_tasks, set_reminder]
    """
    
    def __init__(self, openai_client: OpenAI):
        self.openai = openai_client
    
    def execute_sequence(
        self,
        intents: List[str],
        context: ConversationContext,
        calendar_service: Any,
        db_session: Any
    ) -> ConversationContext:
        """
        Execute handlers for each intent in sequence
        
        Args:
            intents: List of intent names in priority order
            context: Conversation context
            calendar_service: Calendar service instance
            db_session: Database session
            
        Returns:
            Updated context with combined response
        """
        
        if not intents:
            # Fallback to continue_conversation
            intents = ["continue_conversation"]
        
        # If only one intent, execute normally
        if len(intents) == 1:
            handler = get_handler(intents[0])
            return handler.execute(context, self.openai, calendar_service, db_session)
        
        # Multiple intents - execute in sequence
        responses = []
        tool_results = []
        
        logger.info(f"🔄 Executing {len(intents)} handlers in sequence: {intents}")
        
        for i, intent in enumerate(intents):
            logger.info(f"  {i+1}. Executing {intent} handler...")
            
            try:
                handler = get_handler(intent)
                context = handler.execute(context, self.openai, calendar_service, db_session)
                
                if context.response:
                    responses.append(context.response)
                
                if context.tool_result:
                    tool_results.append(f"{intent}: {context.tool_result}")
                
            except Exception as e:
                logger.info(f"  ❌ Error executing {intent} handler: {e}")
                continue
        
        # Combine responses naturally
        if len(responses) > 1:
            context.response = self._combine_responses(responses, context.emotion, intents)
        elif responses:
            context.response = responses[0]
        else:
            context.response = "I'm here to help! How can I assist you?"
        
        # Combine tool results
        if tool_results:
            context.tool_result = " | ".join(tool_results)
        
        return context
    
    def _combine_responses(
        self,
        responses: List[str],
        emotion: str,
        intents: List[str]
    ) -> str:
        """
        Use LLM to combine multiple handler responses into one cohesive message
        
        Args:
            responses: List of individual handler responses
            emotion: User's detected emotion
            intents: List of intents that were handled
            
        Returns:
            Combined, natural-sounding response
        """
        
        prompt = f"""You are combining multiple responses into one cohesive message.

User's emotion: {emotion}
Intents handled: {', '.join(intents)}

Individual responses:
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(responses))}

Combine these into ONE natural, flowing response that:
1. Addresses the emotional aspect first (if present)
2. Then handles the practical tasks
3. Maintains a warm, supportive tone
4. Doesn't feel robotic or repetitive
5. Flows naturally as if written by one person

Keep it concise (2-4 sentences max). Use emojis if appropriate.

Combined response:"""

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            combined = response.choices[0].message.content.strip()
            logger.info("Combined {len(responses)} responses into one")
            return combined
            
        except Exception as e:
            logger.error("Error combining responses: {e}")
            # Fallback: join with newlines
            return "\n\n".join(responses)
