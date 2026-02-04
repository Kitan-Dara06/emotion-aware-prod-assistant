import logging
from openai import OpenAI
from .context import ConversationContext

logger = logging.getLogger(__name__)

class ActionRouter:
    """Routes user input to appropriate handler using LLM intelligence"""
    
    OVERWHELM_EMOTIONS = {"overwhelm", "stress", "anxiety", "fear", "nervousness"}
    
    def __init__(self, openai_client: OpenAI):
        self.openai = openai_client
    
    def route(self, user_input: str, context: ConversationContext) -> str:
        """Determine which action to take"""
        
        # 1. EMOTION CHECK FIRST
        # If user is overwhelmed, prioritize support over productivity
        if context.emotion in self.OVERWHELM_EMOTIONS:
            return "overwhelm"
        
        # 2. INTENT CHECK (LLM)
        return self._llm_route(user_input, context)
    
    def _llm_route(self, user_input: str, context: ConversationContext) -> str:
        """Use LLM to determine action"""
        prompt = f"""Given this user message and emotion, determine the best action.
        
User message: "{user_input}"
Detected emotion: {context.emotion}

Choose ONE action from this list:
- schedule_event (wants to book/create event)
- set_reminder (wants to be reminded)
- reschedule_event (wants to change event time)
- vent (wants to express feelings, complain)
- answer_question (factual question)
- give_advice (asking for guidance/opinion)
- fetch_info (needs resources/search)
- summarize_input (gave a long text to summarize)
- do_nothing (casual/joke/greeting)

Return ONLY the exact action name from the list. If unsure, return continue_conversation."""

        try:
            response = self.openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=20
            )
            
            action = response.choices[0].message.content.strip().lower()
            
            # Allow "continue_conversation" as fallback
            valid_actions = {
                "schedule_event", "set_reminder", "reschedule_event",
                "vent", "answer_question", "give_advice", "fetch_info",
                "summarize_input", "do_nothing", "continue_conversation"
            }
            
            return action if action in valid_actions else "continue_conversation"
            
        except Exception as e:
            logger.info(f"Routing error: {e}")
            return "continue_conversation"
    
    def route_multi(self, user_input: str, context: 'ConversationContext') -> list[str]:
        """
        Detect multiple intents in a single message
        
        Returns list of intents in priority order:
        1. Emotional support (overwhelm, talk_only) - Always first
        2. Productivity (schedule, remind, prioritize)
        3. Conversation (vent, advice, questions)
        
        Examples:
        - "I'm stressed and need to schedule a meeting" → ["overwhelm", "schedule_event"]
        - "Help me prioritize tasks and set a reminder" → ["prioritize_tasks", "set_reminder"]
        """
        
        prompt = f"""Analyze this message for MULTIPLE intents. Return them in priority order.

Message: "{user_input}"
Emotion: {context.emotion or 'neutral'}

Available intents:
- overwhelm: User feeling overwhelmed, needs grounding
- talk_only: User needs emotional support, just listening
- prioritize_tasks: User has multiple tasks, needs help prioritizing
- schedule_event: User wants to schedule/create calendar event
- reschedule_event: User wants to change existing event time
- set_reminder: User wants a reminder for something
- vent: User needs to vent frustrations
- give_advice: User asking for advice/suggestions
- answer_question: User asking a factual question
- continue_conversation: General conversation

Priority rules:
1. Emotional support FIRST (overwhelm, talk_only)
2. Then productivity (schedule, remind, prioritize)
3. Then conversation (vent, advice, questions)

Return ONLY a JSON array of intent strings, ordered by priority:
["intent1", "intent2", ...]

If only one intent, return single-item array: ["intent"]

Examples:
Input: "I'm feeling overwhelmed and need to schedule a meeting tomorrow"
Output: ["overwhelm", "schedule_event"]

Input: "Help me prioritize my tasks and remind me to call mom"
Output: ["prioritize_tasks", "set_reminder"]

Input: "I'm stressed"
Output: ["overwhelm"]

Return JSON array:"""

        try:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100
            )
            
            raw = response.choices[0].message.content.strip()
            
            # Extract JSON array
            import re
            import json
            
            # Find JSON array in response
            match = re.search(r'\[.*?\]', raw, re.DOTALL)
            if match:
                intents = json.loads(match.group())
                
                # Validate intents
                valid_intents = [
                    "overwhelm", "talk_only", "prioritize_tasks",
                    "schedule_event", "reschedule_event", "set_reminder",
                    "vent", "give_advice", "answer_question", "continue_conversation"
                ]
                
                intents = [i for i in intents if i in valid_intents]
                
                if intents:
                    logger.info("Multi-intent detected: {intents}")
                    return intents
            
            # Fallback to single intent
            return [self.route(user_input, context)]
            
        except Exception as e:
            logger.info(f"Multi-intent routing error: {e}")
            # Fallback to single intent
            return [self.route(user_input, context)]