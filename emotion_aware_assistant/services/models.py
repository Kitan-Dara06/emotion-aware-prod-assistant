from sqlalchemy import Column, String, Integer, DateTime, Text
from emotion_aware_assistant.services.database import Base
from datetime import datetime

class UserToken(Base):
    """OAuth tokens for Google Calendar integration"""
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    token = Column(String)
    refresh_token = Column(String)
    token_uri = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    scopes = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationMessage(Base):
    """Individual conversation messages for history tracking"""
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=True)  # Optional: link to user
    session_id = Column(String, index=True)  # Group messages by conversation session
    
    # Message content
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text)
    
    # AI analysis
    emotion = Column(String)
    suggested_action = Column(String)
    tool_result = Column(Text, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "emotion": self.emotion,
            "suggested_action": self.suggested_action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
