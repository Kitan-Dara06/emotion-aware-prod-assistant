import logging
from .base import BaseHandler
from emotion_aware_assistant.core.context import ConversationContext
from openai import OpenAI
from typing import Any, Dict
import json
import re

logger = logging.getLogger(__name__)

class ScheduleHandler(BaseHandler):
    """
    Handles event scheduling
    
    Logic:
    1. Use LLM to extract event details (what + when)
    2. Validate extracted data
    3. Call calendar service to create event
    4. Return confirmation or error message
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        """Execute event scheduling with conflict detection, duration, and recurrence support"""
        
        # 1. Extract event details (now includes duration and recurrence)
        event_data = self._extract_event_details(openai_client, context)
        
        if "error" in event_data:
            context.response = event_data["error"]
            return context
        
        event_name = event_data.get("event")
        event_time = event_data.get("time")
        duration = event_data.get("duration")  # NEW: Optional duration
        recurrence = event_data.get("recurrence")  # NEW: Optional recurrence
        
        if not event_name or not event_time:
            context.response = "I need both what you want to schedule and when. Could you provide both?"
            return context
        
        # 2. Get user email from context (required for calendar access)
        user_email = context.user_email
        
        if not user_email:
            # No calendar access - provide helpful message
            if recurrence:
                context.response = f"I'd love to schedule '{event_name}' {recurrence} at {event_time}, but I need you to connect your Google Calendar first."
            elif duration:
                context.response = f"I'd love to schedule a {duration} '{event_name}' at {event_time}, but I need you to connect your Google Calendar first."
            else:
                context.response = f"I'd love to schedule '{event_name}' for {event_time}, but I need you to connect your Google Calendar first."
            context.tool_result = None
            return context
        
        # 3. Check for conflicts (NEW)
        try:
            from emotion_aware_assistant.services.calendar import check_conflicts, parse_duration
            import dateparser
            import pytz
            from datetime import timedelta
            
            # Parse the time to check for conflicts
            lagos_tz = pytz.timezone("Africa/Lagos")
            start_time = dateparser.parse(
                event_time,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'TIMEZONE': 'Africa/Lagos',
                    'RETURN_AS_TIMEZONE_AWARE': True
                }
            )
            
            if start_time:
                # Calculate end time based on duration
                event_duration = parse_duration(duration) if duration else timedelta(hours=1)
                end_time = start_time + event_duration
                
                # Check for conflicts
                conflicts = check_conflicts(user_email, start_time, end_time)
                
                if conflicts:
                    conflict_names = [c['summary'] for c in conflicts]
                    context.response = f"⚠️ You already have {', '.join(conflict_names)} at that time. Want to reschedule that first?"
                    context.tool_result = "conflict_detected"
                    return context
        except Exception as e:
            logger.info(f"Conflict check failed: {e}")
            # Continue with scheduling even if conflict check fails
        
        # 4. Attempt to create calendar event
        try:
            from emotion_aware_assistant.services.calendar import create_event
            
            # Pass duration and recurrence to calendar service
            result = create_event(
                email=user_email,
                event=event_name,
                time=event_time,
                repeat=recurrence,  # Pass recurrence pattern
                duration=duration    # Pass duration
            )
            
            # Success!
            context.scheduled_events.append({
                "event": event_name,
                "time": event_time,
                "duration": duration,
                "recurrence": recurrence
            })
            context.tool_result = result
            
            if recurrence:
                context.response = f"✅ Scheduled '{event_name}' {recurrence} at {event_time}!"
            elif duration:
                context.response = f"✅ Scheduled {duration} '{event_name}' at {event_time}!"
            else:
                context.response = self._generate_confirmation_response(
                    openai_client, context, event_name, event_time, "scheduled"
                )
            
        except Exception as e:
            logger.error("Error creating event: {e}")
            context.response = f"Sorry, I couldn't schedule that event: {str(e)}"
            context.tool_result = None
        
        return context
    
    def _extract_event_details(self, openai_client: OpenAI, context: ConversationContext) -> Dict:
        """
        Use LLM to extract structured event data from natural language
        
        Now extracts:
        - event: What to schedule
        - time: When to schedule it
        - duration: How long (optional)
        - recurrence: Repeat pattern (optional)
        
        Examples:
        - "Schedule team meeting tomorrow at 3pm" → {"event": "team meeting", "time": "tomorrow at 3pm"}
        - "Schedule 2-hour workshop tomorrow at 3pm" → {"event": "workshop", "time": "tomorrow at 3pm", "duration": "2 hours"}
        - "Schedule standup every Monday at 9am" → {"event": "standup", "time": "Monday at 9am", "recurrence": "weekly"}
        """
        full_input = self._get_full_input(context)
        
        prompt = f"""Extract event scheduling information from this message.

Message: {full_input}

Return ONLY valid JSON with these fields:
- "event": what the user wants to do (brief description)
- "time": when they want to do it (preserve exact time expression)
- "duration": how long the event is (e.g., "2 hours", "30 minutes") - OPTIONAL, omit if not mentioned
- "recurrence": repeat pattern (e.g., "daily", "weekly", "monthly") - OPTIONAL, omit if not mentioned

Examples:
1. "Schedule team meeting tomorrow at 3pm"
   → {{"event": "team meeting", "time": "tomorrow at 3pm"}}

2. "Schedule 2-hour workshop tomorrow at 3pm"
   → {{"event": "workshop", "time": "tomorrow at 3pm", "duration": "2 hours"}}

3. "Schedule standup every Monday at 9am"
   → {{"event": "standup", "time": "Monday at 9am", "recurrence": "weekly"}}

4. "Daily check-in at 10am"
   → {{"event": "check-in", "time": "10am", "recurrence": "daily"}}

Do NOT add any explanation or extra text. Return ONLY the JSON."""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200
            )
            
            # Extract JSON from response
            raw_output = response.choices[0].message.content
            match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
            
            if not match:
                return {"error": "I couldn't understand what you want to schedule. Could you rephrase?"}
            
            event_data = json.loads(match.group())
            
            # Log extracted data
            logger.info("Extracted event data: {event_data}")
            
            return event_data
            
        except json.JSONDecodeError:
            return {"error": "I had trouble parsing the event details. Could you be more specific?"}
        except Exception as e:
            logger.error(f"Error extracting event: {e}")
            return {"error": "Something went wrong. Could you try again?"}
    
    def _generate_confirmation_response(self, openai_client: OpenAI, context: ConversationContext,
                                       event_name: str, event_time: str, action: str) -> str:
        """
        Generate a natural, emotion-aware confirmation message
        
        Args:
            event_name: What was scheduled/rescheduled
            event_time: When it's scheduled for
            action: "scheduled" or "rescheduled"
        """
        emotion = context.emotion or "neutral"
        
        prompt = f"""You just successfully {action} an event for the user.

Event: {event_name}
Time: {event_time}
User's emotion: {emotion}

Generate a warm, natural confirmation message. Consider their emotional state:
- If stressed/overwhelmed: Be reassuring, acknowledge you're helping lighten their load
- If excited/happy: Match their energy
- If neutral: Be friendly and helpful

Keep it brief (1-2 sentences). Use emojis if appropriate.

Examples:
- "Great! I've added that to your calendar. Hope that helps ease your mind a bit 😊"
- "Done! Your {event_name} is set for {event_time}. One less thing to worry about!"
- "All set! Looking forward to your {event_name} 🎉"

Generate confirmation:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # More creative for natural responses
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating confirmation: {e}")
            # Fallback to simple confirmation
            return f"✅ {action.capitalize()}: {event_name} at {event_time}"


class ReminderHandler(BaseHandler):
    """
    Handles reminder creation
    
    Logic:
    1. Extract reminder details (what + when)
    2. Store in context (for now - could integrate with calendar/notification service)
    3. Return confirmation
    
    Note: This is simpler than scheduling because reminders don't need calendar API
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI, 
                calendar_service: Any, db_session: Any) -> ConversationContext:
        """Execute reminder creation - creates a calendar event with notification"""
        
        # 1. Extract reminder details
        reminder_data = self._extract_reminder_details(openai_client, context)
        
        if "error" in reminder_data:
            context.response = reminder_data["error"]
            return context
        
        reminder_text = reminder_data.get("reminder")
        reminder_time = reminder_data.get("time")
        
        if not reminder_text or not reminder_time:
            context.response = "I need both what to remind you about and when. Could you provide both?"
            return context
        
        # 2. Get user email for calendar access
        user_email = context.user_email
        
        if not user_email:
            # No calendar access - just acknowledge
            context.response = f"I'll remind you to {reminder_text} at {reminder_time}! (Connect Google Calendar for actual notifications)"
            context.tool_result = f"Reminder set: {reminder_text} at {reminder_time}"
            return context
        
        # 3. Create calendar event with reminder
        try:
            from emotion_aware_assistant.services.calendar import create_event
            
            # Create a short event (15 min) with notification
            result = create_event(
                email=user_email,
                event=f"⏰ Reminder: {reminder_text}",
                time=reminder_time,
                duration="15 minutes"  # Short reminder event
            )
            
            # Success!
            context.response = self._generate_reminder_confirmation(
                openai_client, context, reminder_text, reminder_time
            )
            context.tool_result = f"Reminder set: {reminder_text} at {reminder_time}"
            
        except Exception as e:
            logger.info(f"Reminder creation error: {e}")
            # Fallback
            context.response = f"I'll remind you to {reminder_text} at {reminder_time}! (Calendar not connected)"
            context.tool_result = f"Reminder set: {reminder_text} at {reminder_time}"
        
        return context
    
    def _extract_reminder_details(self, openai_client: OpenAI, context: ConversationContext) -> Dict:
        """
        Extract reminder details from natural language
        
        Example:
        Input: "Remind me to call mom at 5pm"
        Output: {"reminder": "call mom", "time": "5pm"}
        """
        full_input = self._get_full_input(context)
        
        prompt = f"""Extract reminder information from this message.

Message: {full_input}

Return ONLY valid JSON with two fields:
- "reminder": what to remind about (brief description)
- "time": when to remind (preserve exact time expression)

Example: {{"reminder": "call mom", "time": "5pm today"}}

Do NOT add any explanation."""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100
            )
            
            raw_output = response.choices[0].message.content
            match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
            
            if not match:
                return {"error": "I couldn't understand what you want to be reminded about."}
            
            return json.loads(match.group())
            
        except Exception as e:
            logger.error(f"Error extracting reminder: {e}")
            return {"error": "Could you rephrase that reminder?"}
    
    def _generate_reminder_confirmation(self, openai_client: OpenAI, context: ConversationContext,
                                       reminder_text: str, reminder_time: str) -> str:
        """Generate natural reminder confirmation"""
        emotion = context.emotion or "neutral"
        
        prompt = f"""You just set a reminder for the user.

Reminder: {reminder_text}
Time: {reminder_time}
User's emotion: {emotion}

Generate a brief, warm confirmation (1 sentence). Match their emotional tone.

Examples:
- "Got it! I'll remind you to {reminder_text} 🔔"
- "All set! You'll get a reminder at {reminder_time}"
- "Done! I've got your back on this one 😊"

Generate confirmation:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=80
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating reminder confirmation: {e}")
            return f"🔔 Got it! I'll remind you to {reminder_text} at {reminder_time}"


class RescheduleHandler(BaseHandler):
    """
    Handles event rescheduling
    
    Logic:
    1. Extract which event to reschedule + new time
    2. Search calendar for matching event
    3. Update event time
    4. Return confirmation
    
    This is the most complex because it requires:
    - Finding the right event (fuzzy matching)
    - Handling ambiguity (multiple matches)
    - Updating existing calendar entry
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        # Step 1: Extract reschedule details
        reschedule_data = self._extract_reschedule_details(openai_client, context)
        
        # Step 2: Validate
        if "error" in reschedule_data:
            context.response = reschedule_data["error"]
            context.tool_result = None
            return context
        
        event_name = reschedule_data.get("event")
        new_time = reschedule_data.get("new_time")
        
        if not event_name or not new_time:
            context.response = "Which event do you want to reschedule, and to when?"
            context.tool_result = None
            return context
        
        # Step 3: Attempt to reschedule
        try:
            # Check if user has calendar access
            if not context.user_email:
                context.response = (
                    f"I'd love to reschedule '{event_name}' to {new_time}, "
                    "but I need you to connect your Google Calendar first."
                )
                context.tool_result = None
                return context
            
            # Call calendar service
            if calendar_service:
                result = calendar_service.update_calendar_event(
                    email=context.user_email,
                    event=event_name,
                    new_time=new_time
                )
                
                # Step 4: Save and return success
                context.rescheduled_events.append({
                    "event": event_name,
                    "new_time": new_time
                })
                context.tool_result = result
                
                # Step 5: Generate natural confirmation
                context.response = self._generate_confirmation_response(
                    openai_client, context, event_name, new_time, "rescheduled"
                )
            else:
                # No calendar service (testing mode)
                context.response = f"📅 Would reschedule: {event_name} to {new_time} (Calendar not connected)"
                context.tool_result = "calendar_service_unavailable"
        
        except Exception as e:
            logger.error("Error rescheduling event: {e}")
            context.response = f"Sorry, I couldn't reschedule that: {str(e)}"
            context.tool_result = None
        
        return context
    
    def _extract_reschedule_details(self, openai_client: OpenAI, context: ConversationContext) -> Dict:
        """
        Extract which event to reschedule and the new time
        
        Example:
        Input: "Move my dentist appointment to Friday at 2pm"
        Output: {"event": "dentist appointment", "new_time": "Friday at 2pm"}
        """
        full_input = self._get_full_input(context)
        
        prompt = f"""Extract rescheduling information from this message.

Message: {full_input}

Return ONLY valid JSON with two fields:
- "event": which event to reschedule (name/description)
- "new_time": when to move it to (preserve exact time expression)

Example: {{"event": "dentist appointment", "new_time": "Friday at 2pm"}}

Do NOT add any explanation."""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150
            )
            
            raw_output = response.choices[0].message.content
            match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
            
            if not match:
                return {"error": "I couldn't understand which event you want to reschedule."}
            
            return json.loads(match.group())
            
        except Exception as e:
            logger.error(f"Error extracting reschedule info: {e}")
            return {"error": "Could you be more specific about what to reschedule?"}
    
    def _generate_confirmation_response(self, openai_client: OpenAI, context: ConversationContext,
                                       event_name: str, event_time: str, action: str) -> str:
        """
        Generate a natural, emotion-aware confirmation message
        (Reused from ScheduleHandler)
        """
        emotion = context.emotion or "neutral"
        
        prompt = f"""You just successfully {action} an event for the user.

Event: {event_name}
New time: {event_time}
User's emotion: {emotion}

Generate a warm, natural confirmation message. Consider their emotional state:
- If stressed/overwhelmed: Be reassuring
- If excited/happy: Match their energy
- If neutral: Be friendly and helpful

Keep it brief (1-2 sentences). Use emojis if appropriate.

Examples:
- "All done! I've moved that to {event_time} for you 😊"
- "Perfect! Your {event_name} is now at {event_time}"
- "Rescheduled! Hope that timing works better for you"

Generate confirmation:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating confirmation: {e}")
            return f"✅ {action.capitalize()}: {event_name} to {event_time}"
