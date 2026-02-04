import logging
from typing import Optional
from openai import OpenAI
from .context import ConversationContext
from .router import ActionRouter
from .multi_handler import MultiHandlerExecutor
from emotion_aware_assistant.services.emotion import detect_emotion
from emotion_aware_assistant.services.conversation import ConversationService
from emotion_aware_assistant.services.vector_memory import VectorMemoryService
from emotion_aware_assistant.handlers import get_handler

logger = logging.getLogger(__name__)

class EmotionAwareAssistant:
    """Main orchestrator for the emotion-aware assistant"""
    
    def __init__(
        self, 
        openai_client: OpenAI, 
        calendar_service, 
        db_session,
        vector_memory: Optional[VectorMemoryService] = None,
        enable_multi_intent: bool = True
    ):
        self.openai = openai_client
        self.calendar = calendar_service
        self.db = db_session
        self.router = ActionRouter(openai_client)
        self.conversation_service = ConversationService(db_session)
        self.vector_memory = vector_memory  # Optional Pinecone integration
        self.enable_multi_intent = enable_multi_intent
        self.multi_handler = MultiHandlerExecutor(openai_client) if enable_multi_intent else None
    
    def process_message(
        self, 
        user_input: str, 
        context: Optional[ConversationContext] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> tuple[ConversationContext, str]:
        """
        Main processing pipeline with hybrid memory (PostgreSQL + Pinecone)
        
        Returns:
            tuple: (updated_context, session_id)
        """
        # Initialize context if new conversation
        if context is None:
            context = ConversationContext(user_input=user_input)
            
            # Load recent history from PostgreSQL if session_id provided
            if session_id:
                context = self.conversation_service.load_history_into_context(
                    session_id, context, max_messages=5
                )
        else:
            context.user_input = user_input
        
        # SEMANTIC MEMORY: Search for similar past conversations
        if self.vector_memory and user_id:
            try:
                similar_context = self.vector_memory.get_conversation_context(
                    current_message=user_input,
                    user_id=user_id,
                    max_context=2
                )
                if similar_context:
                    logger.info(f"📚 Found relevant context from past conversations")
                    # Add to context for handler to use
                    context.history.insert(0, f"[CONTEXT] {similar_context}")
            except Exception as e:
                logger.warning("Vector memory search failed: {e}")
        
        # 1. Detect emotion
        context.emotion = detect_emotion(user_input)
        context.add_emotion(context.emotion)
        
        # 2. Determine action(s) - Multi-intent or single intent
        if self.enable_multi_intent and self.multi_handler:
            # Multi-intent detection
            intents = self.router.route_multi(user_input, context)
            
            if len(intents) > 1:
                # Multiple intents - use multi-handler
                logger.info("Processing {len(intents)} intents: {intents}")
                context = self.multi_handler.execute_sequence(
                    intents, context, self.calendar, self.db
                )
                # Store all intents
                context.suggested_action = " + ".join(intents)
            else:
                # Single intent - use regular flow
                context.suggested_action = intents[0] if intents else "continue_conversation"
                handler = get_handler(context.suggested_action)
                context = handler.execute(context, self.openai, self.calendar, self.db)
        else:
            # Single intent mode (legacy)
            context.suggested_action = self.router.route(user_input, context)
            handler = get_handler(context.suggested_action)
            context = handler.execute(context, self.openai, self.calendar, self.db)
        
        # 4. Update history (in-memory)
        context.add_to_history(user_input)
        if context.response:
            context.add_to_history(context.response)
        
        # 5. Save to PostgreSQL
        saved_message = self.conversation_service.save_message(context, session_id)
        final_session_id = saved_message.session_id
        
        # 6. SEMANTIC MEMORY: Save to Pinecone for future semantic search
        if self.vector_memory and user_id and context.response:
            try:
                self.vector_memory.save_conversation(
                    user_id=user_id,
                    user_message=user_input,
                    assistant_response=context.response,
                    emotion=context.emotion,
                    action=context.suggested_action,
                    session_id=final_session_id
                )
            except Exception as e:
                logger.warning("Vector memory save failed: {e}")
        
        return context, final_session_id