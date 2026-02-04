from sqlalchemy.orm import Session
from emotion_aware_assistant.services.models import ConversationMessage
from emotion_aware_assistant.core.context import ConversationContext
from typing import List, Optional
import uuid

class ConversationService:
    """Service for managing conversation history in database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_message(self, context: ConversationContext, session_id: Optional[str] = None) -> ConversationMessage:
        """Save a conversation turn to database"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        message = ConversationMessage(
            user_email=context.user_email,
            session_id=session_id,
            user_message=context.user_input,
            assistant_response=context.response,
            emotion=context.emotion,
            suggested_action=context.suggested_action,
            tool_result=context.tool_result
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[ConversationMessage]:
        """Retrieve conversation history for a session"""
        messages = self.db.query(ConversationMessage)\
            .filter(ConversationMessage.session_id == session_id)\
            .order_by(ConversationMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return list(reversed(messages))  # Return in chronological order
    
    def get_user_history(self, user_email: str, limit: int = 20) -> List[ConversationMessage]:
        """Retrieve recent conversation history for a user"""
        messages = self.db.query(ConversationMessage)\
            .filter(ConversationMessage.user_email == user_email)\
            .order_by(ConversationMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return list(reversed(messages))
    
    def load_history_into_context(self, session_id: str, context: ConversationContext, max_messages: int = 5):
        """Load recent history from database into context"""
        messages = self.get_session_history(session_id, limit=max_messages)
        
        # Build history list
        history = []
        for msg in messages:
            if msg.user_message:
                history.append(msg.user_message)
            if msg.assistant_response:
                history.append(msg.assistant_response)
        
        # Keep only last N messages
        context.history = history[-max_messages:]
        
        # Load emotion history
        for msg in messages:
            if msg.emotion and msg.timestamp:
                context.emotion_history.append({
                    "timestamp": msg.timestamp.isoformat(),
                    "emotion": msg.emotion
                })
        
        return context
    
    def load_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """
        Load conversation history for API endpoint
        Returns list of message dicts
        """
        # Use user_id as session_id for now
        messages = self.get_session_history(user_id, limit=limit)
        
        # Convert to dict format
        history = []
        for msg in messages:
            if msg.user_message:
                history.append({
                    "role": "user",
                    "content": msg.user_message,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "emotion": msg.emotion
                })
            if msg.assistant_response:
                history.append({
                    "role": "assistant",
                    "content": msg.assistant_response,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                })
        
        return history

