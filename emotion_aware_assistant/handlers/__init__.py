import logging
from typing import Dict, Type
from .base import BaseHandler
from .conversation import (
    VentHandler,
    AnswerQuestionHandler,
    GiveAdviceHandler,
    DoNothingHandler,
    FetchInfoHandler,
    ContinueConversationHandler,
    SummarizeInputHandler
)
from .productivity import (
    ScheduleHandler,
    ReminderHandler,
    RescheduleHandler
)
from .emotion import (

logger = logging.getLogger(__name__)
    OverwhelmHandler,
    PrioritizeTasksHandler,
    TalkOnlyHandler
)

# Handler registry - maps action names to handler classes
HANDLERS: Dict[str, Type[BaseHandler]] = {
    # Conversation handlers
    "vent": VentHandler,
    "answer_question": AnswerQuestionHandler,
    "give_advice": GiveAdviceHandler,
    "do_nothing": DoNothingHandler,
    "fetch_info": FetchInfoHandler,
    "continue_conversation": ContinueConversationHandler,
    "summarize_input": SummarizeInputHandler,
    
    # Productivity handlers
    "schedule_event": ScheduleHandler,
    "set_reminder": ReminderHandler,
    "reschedule_event": RescheduleHandler,
    
    # Emotion handlers
    "overwhelm": OverwhelmHandler,
    "prioritize_tasks": PrioritizeTasksHandler,
    "talk_only": TalkOnlyHandler,
}

def get_handler(action: str) -> BaseHandler:
    """
    Get handler instance for the given action
    
    Args:
        action: Action name (e.g., "vent", "schedule_event")
    
    Returns:
        Handler instance
    """
    handler_class = HANDLERS.get(action)
    
    if handler_class is None:
        # Fallback to continue conversation if action not found
        logger.warning("Handler not found for action: {action}, using ContinueConversationHandler")
        handler_class = ContinueConversationHandler
    
    return handler_class()
