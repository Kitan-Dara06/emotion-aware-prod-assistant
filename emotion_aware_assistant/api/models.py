from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's message")
    user_email: Optional[str] = Field(None, description="User's email (for calendar access)")
    user_id: Optional[str] = Field(None, description="User ID for conversation history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'm feeling really overwhelmed with all my tasks",
                "user_email": "user@example.com",
                "user_id": "user123"
            }
        }

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Assistant's response")
    emotion: Optional[str] = Field(None, description="Detected emotion")
    action: Optional[str] = Field(None, description="Action taken")
    tool_result: Optional[str] = Field(None, description="Result from tool execution")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I can hear that you're feeling really overwhelmed. Let's take a breath first...",
                "emotion": "overwhelm",
                "action": "overwhelm",
                "tool_result": "overwhelm_support_provided"
            }
        }

class HistoryRequest(BaseModel):
    """Request model for getting conversation history"""
    user_id: str = Field(..., description="User ID")
    limit: Optional[int] = Field(10, description="Number of messages to retrieve")

class HistoryResponse(BaseModel):
    """Response model for conversation history"""
    messages: List[Dict] = Field(..., description="List of conversation messages")
    total: int = Field(..., description="Total number of messages")
