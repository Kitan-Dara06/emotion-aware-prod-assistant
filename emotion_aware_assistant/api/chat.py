import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from openai import OpenAI

from emotion_aware_assistant.api.models import (
    ChatRequest, 
    ChatResponse,
    HistoryRequest,
    HistoryResponse
)
from emotion_aware_assistant.core.assistant import EmotionAwareAssistant
from emotion_aware_assistant.core.context import ConversationContext
from emotion_aware_assistant.services.database import get_session_local
from emotion_aware_assistant.services.conversation import ConversationService
from emotion_aware_assistant.services.vector_memory import VectorMemoryService
from emotion_aware_assistant.services.calendar import (
    get_calendar_service,
    create_event,
    update_calendar_event
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Pinecone vector memory (optional - only if API key is set)
vector_memory = None
pinecone_api_key = os.getenv("PINECONE_API_KEY")
if pinecone_api_key:
    try:
        vector_memory = VectorMemoryService(
            pinecone_api_key=pinecone_api_key,
            openai_client=openai_client,
            index_name=os.getenv("PINECONE_INDEX_NAME", "emotion-assistant")
        )
        logger.info("Pinecone vector memory initialized")
    except Exception as e:
        logger.warning("Pinecone initialization failed: {e}")
        logger.info("   Continuing without semantic memory...")
else:
    logger.warning("PINECONE_API_KEY not set - semantic memory disabled")

# Dependency to get database session
def get_db():
    """Get database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint - processes user message and returns response
    
    Flow:
    1. Create conversation context
    2. Load conversation history (if user_id provided)
    3. Process message through EmotionAwareAssistant
    4. Save conversation to database
    5. Return response
    """
    try:
        # Step 1: Create context
        context = ConversationContext(
            user_input=request.message,
            user_email=request.user_email
        )
        
        # Step 2: Get calendar service (if user has email)
        calendar_service = None
        if request.user_email:
            try:
                calendar_service = get_calendar_service(request.user_email)
            except Exception as e:
                logger.warning("Calendar service unavailable: {e}")
        
        # Step 3: Initialize assistant
        assistant = EmotionAwareAssistant(
            openai_client=openai_client,
            calendar_service=calendar_service,
            db_session=db,
            vector_memory=vector_memory  # Pass Pinecone service
        )
        
        # Step 4: Process message with user_id for semantic memory
        result_context, session_id = assistant.process_message(
            user_input=request.message,
            context=context,
            session_id=request.user_id,  # Use user_id as session_id
            user_id=request.user_id  # For vector memory filtering
        )
        
        # Step 5: Return response
        return ChatResponse(
            response=result_context.response or "I'm here to help!",
            emotion=result_context.emotion,
            action=result_context.suggested_action,
            tool_result=result_context.tool_result
        )
        
    except Exception as e:
        logger.error("Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )

@router.post("/history", response_model=HistoryResponse)
async def get_history(request: HistoryRequest, db: Session = Depends(get_db)):
    """
    Get conversation history for a user
    """
    try:
        conv_service = ConversationService(db)
        messages = conv_service.load_history(request.user_id, limit=request.limit)
        
        return HistoryResponse(
            messages=messages,
            total=len(messages)
        )
        
    except Exception as e:
        logger.error("Error fetching history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching history: {str(e)}"
        )

@router.delete("/history/{user_id}")
async def clear_history(user_id: str, db: Session = Depends(get_db)):
    """
    Clear conversation history for a user
    """
    try:
        conv_service = ConversationService(db)
        # Delete all messages for user
        from emotion_aware_assistant.services.models import ConversationMessage
        db.query(ConversationMessage).filter_by(user_id=user_id).delete()
        db.commit()
        
        return {"message": f"History cleared for user {user_id}"}
        
    except Exception as e:
        logger.error("Error clearing history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing history: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "emotion-aware-assistant",
        "version": "2.0.0"
    }
