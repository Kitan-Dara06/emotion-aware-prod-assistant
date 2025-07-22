from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.config import api_key
# classifier = pipeline(
#     "text-classification",
#     model="SamLowe/roberta-base-go_emotions",
#     top_k=1,
#     truncation=True
# )


# def detect_emotion(text):
#     return classifier(text)[0][0]['label']  switching to open ai classfication to reduce heaviness on deployment

client = OpenAI(api_key=api_key)

GO_EMOTION_LIST = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval", "disgust",
    "embarrassment", "excitement", "fear", "gratitude", "grief", "joy", "love",
    "nervousness", "optimism", "pride", "realization", "relief", "remorse",
    "sadness", "surprise", "neutral"
]

def detect_emotion(text: str) -> str:
    prompt = f"""
You're an emotion classification assistant. Given the user's message, identify their dominant emotion.
ONLY choose from this list of 28 possible emotions (no freeform words):

{', '.join(GO_EMOTION_LIST)}

User message: "{text}"

Return just one word — the most likely emotion from the list above.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # Deterministic, since this is classification
    )
    return response.choices[0].message.content.strip().lower()
