from .base import BaseHandler
from emotion_aware_assistant.core.context import ConversationContext    
from openai import OpenAI
from typing import Any

class VentHandler(BaseHandler):
    """Handles venting - validates feelings without problem-solving"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""You're a compassionate and emotionally intelligent assistant.
{context.user_profile or "You prefer warm, human responses."}

The user is venting. Don't try to fix or explain anything. 
Just reflect their feelings and validate them.
Be gentle, nonjudgmental, and empathetic. Let them feel seen."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=300
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class GiveAdviceHandler(BaseHandler):
    """Provides thoughtful guidance without being forceful"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = """The user is asking for advice on what to do in their situation.

Give a thoughtful, emotionally aware answer. It's okay to offer some light direction — just don't be forceful.

Gently guide them by highlighting trade-offs or options. Encourage reflection while offering support."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=300
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class AnswerQuestionHandler(BaseHandler):
    """Handles factual questions with emotional awareness"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""You're an assistant who provides helpful, emotionally aware information.
{context.user_profile or "You prefer warm, human responses."}

The user wants facts, suggestions, or resources.
Be accurate and human. If it's a list or recommendation, briefly explain how it helps."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=300
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class DoNothingHandler(BaseHandler):
    """Handles casual or non-actionable input in a friendly way"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""The user just said something casual or friendly, like a joke, meme, or light comment.
{context.user_profile or "You prefer warm, human responses."}

Respond in a relaxed, human tone. Acknowledge their message, and if it feels natural, 
ask a playful follow-up or express curiosity.
No advice or emotion processing here — just chill, friendly chat."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=200
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class FetchInfoHandler(BaseHandler):
    """Provides information and resources"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""You're an assistant who provides helpful, emotionally aware information.
{context.user_profile or "You prefer warm, human responses."}

The user wants facts, suggestions, or resources.
Be accurate and human. If it's a list or recommendation, briefly explain how it helps."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=350
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class ContinueConversationHandler(BaseHandler):
    """Keeps the conversation flowing naturally"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""You are a caring assistant continuing a heartful conversation.

The user's current emotion is: {context.emotion or "neutral"}
Your job is to keep the conversation flowing naturally with empathy.

Be warm, emotionally aware, and ask a gentle follow-up.
Do not give advice or solutions here — just invite them to share more."""
        
        full_input = self._get_full_input(context)
        response = self._call_llm(
            openai_client, system_prompt, full_input, max_tokens=250
        )
        
        context.response = response
        context.tool_result = None
        
        return context


class SummarizeInputHandler(BaseHandler):
    """Summarizes long user input"""
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        user_input = context.user_input or ""
        
        # Check if input is too long
        if len(user_input.split()) > 500:
            context.response = (
                "That's quite a lot to process at once. "
                "Could you shorten it to under 500 words so I can better understand and help?"
            )
            context.tool_result = None
            return context
        
        system_prompt = """You help users process big thoughts clearly.

Summarize what the user shared into a short, focused overview.

Be clear and emotionally aware, but don't reflect past chats or context."""
        
        response = self._call_llm(
            openai_client, system_prompt, user_input, 
            model="gpt-4o", max_tokens=700
        )
        
        context.response = response
        context.tool_result = None
        
        return context
