# DEPRECATED: This file is from the old LangGraph implementation
# New implementation is in core/assistant.py
# Keeping minimal version for backward compatibility with old nodes

import logging
from openai import OpenAI
from emotion_aware_assistant.config import api_key
from emotion_aware_assistant.services.emotion import detect_emotion
import json
import re

logger = logging.getLogger(__name__)

client = OpenAI(api_key=api_key)

def respond_with_empathy(text: str) -> dict:
    """
    DEPRECATED: Old LangGraph version
    Use core.assistant.EmotionAwareAssistant instead
    
    Kept for backward compatibility with old nodes
    """
    logger.warning("WARNING: Using deprecated respond_with_empathy(). Migrate to core.assistant.EmotionAwareAssistant")
    
    # Detect emotion
    emotion = detect_emotion(text)
    
    # Simple prompt for emotion + goal + action
    prompt = f"""Analyze this user message and respond with JSON.

User message: "{text}"
Detected emotion: {emotion}

Return ONLY valid JSON with these fields:
{{
    "emotion": "{emotion}",
    "goal": "what the user wants to achieve (1 sentence)",
    "suggested_action": "one of: vent, schedule_event, set_reminder, reschedule_event, answer_question, give_advice, fetch_info, do_nothing, continue_conversation"
}}

Return JSON:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        raw_output = response.choices[0].message.content
        
        # Extract JSON
        match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return result
        else:
            return {
                "emotion": emotion,
                "goal": "continue conversation",
                "suggested_action": "continue_conversation"
            }
            
    except Exception as e:
        logger.error(f"Error in respond_with_empathy: {e}")
        return {
            "emotion": emotion,
            "goal": "continue conversation",
            "suggested_action": "continue_conversation"
        }
