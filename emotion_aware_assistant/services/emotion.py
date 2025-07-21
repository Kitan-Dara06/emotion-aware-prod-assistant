from emotion_aware_assistant.gloabal_import import *

# classifier = pipeline(
#     "text-classification",
#     model="SamLowe/roberta-base-go_emotions",
#     top_k=1,
#     truncation=True
# )


# def detect_emotion(text):
#     return classifier(text)[0][0]['label']  switching to open ai classfication to reduce heaviness on deployment

client = OpenAI(api_key=api_key)
