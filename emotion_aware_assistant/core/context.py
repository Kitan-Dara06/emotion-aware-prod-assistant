from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class ConversationContext:
    user_input: str
    user_email: Optional[str] = None

    emotion: Optional[str] = None
    goal: Optional[str] = None
    suggested_action: Optional[str] = None

    history: List[str] = field(default_factory=list)
    emotion_history: List[Dict[str, str]] = field(default_factory=list)
    reminders: List[Dict[str, str]] = field(default_factory=list)
    scheduled_events: List[Dict[str, str]] = field(default_factory=list)
    rescheduled_events: List[Dict[str, str]] = field(default_factory=list)

    response: Optional[str] = None
    tool_result: Optional[str] = None
    user_profile: Optional[str] = None
    timezone: str = "Africa/Lagos"

    def add_to_history(self, message: str, max_history: int = 5):
        """Add message to history with automatic trimming"""
        if message:
            self.history.append(message)
            if len(self.history) > max_history:
                self.history = self.history[-max_history:]
    
    def add_emotion(self, emotion: str):
        """Track emotion with timestamp"""
        if emotion:
            self.emotion_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "emotion": emotion
            })