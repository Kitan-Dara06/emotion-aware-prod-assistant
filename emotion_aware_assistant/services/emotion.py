import logging
from openai import OpenAI
from emotion_aware_assistant.config import api_key
from dotenv import load_dotenv
load_dotenv()
import os
from emotion_aware_assistant.utils.rate_limiter import rate_limited

logger = logging.getLogger(__name__)
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or api_key)

# 28 emotions from go_emotions dataset
GO_EMOTION_LIST = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval", "disgust",
    "embarrassment", "excitement", "fear", "gratitude", "grief", "joy", "love",
    "nervousness", "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise", "neutral"
]

@rate_limited
def detect_emotion(user_input: str) -> str:
    """
    Detect emotion from text using OpenAI GPT-3.5-turbo
    
    Args:
        text: User's message
    
    Returns:
        One of 28 emotions from GO_EMOTION_LIST
    """
    prompt = f"""You're an emotion classification assistant. Given the user's message, identify their dominant emotion.
ONLY choose from this list of 28 possible emotions (no freeform words):

{', '.join(GO_EMOTION_LIST)}

User message: "{text}"

Return just one word — the most likely emotion from the list above."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic, since this is classification
            max_tokens=20
        )
        
        emotion = response.choices[0].message.content.strip().lower()
        
        # Log if emotion is unexpected, but trust the LLM's judgment
        if emotion not in GO_EMOTION_LIST:
            logger.warning("LLM returned unexpected emotion: '{emotion}' (not in GO_EMOTION_LIST)")
            logger.info(f"   Trusting LLM's judgment - this might be a valid nuanced emotion")
        
        return emotion
            
    except Exception as e:
        logger.error("Error detecting emotion: {e}")
        # Only fallback to neutral on technical errors (API failure, etc.)
        return "neutral"
