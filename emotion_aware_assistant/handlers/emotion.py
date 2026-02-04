import logging
from .base import BaseHandler
from emotion_aware_assistant.core.context import ConversationContext
from openai import OpenAI
from typing import Any, List, Dict
import json
import re

logger = logging.getLogger(__name__)

class OverwhelmHandler(BaseHandler):
    """
    Handles overwhelm/stress situations
    
    Logic:
    1. Acknowledge the overwhelm (validation)
    2. Offer grounding techniques
    3. Suggest breaking down tasks
    4. Provide emotional support
    
    This is the most important handler - it's triggered automatically
    when router detects overwhelm emotions (stress, anxiety, fear, etc.)
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        # Build empathetic response with grounding techniques
        system_prompt = f"""You're a compassionate assistant helping someone who feels overwhelmed.

User's emotion: {context.emotion}
User's message: {context.user_input}

Your response should:
1. VALIDATE their feelings (acknowledge the overwhelm is real)
2. GROUND them (suggest a quick breathing exercise or grounding technique)
3. SIMPLIFY (offer to help break things down into smaller steps)
4. REASSURE (remind them they don't have to do everything at once)

Tone: Warm, calm, non-judgmental, like a supportive friend
Length: 2-3 sentences
Include: One actionable grounding technique (e.g., "Take 3 deep breaths")

Example:
"I can hear that you're feeling really overwhelmed right now, and that's completely valid. 
Let's take a moment — try taking three slow, deep breaths with me. 
Once you're ready, we can break this down into smaller, manageable steps together. You've got this 💙"

Generate response:"""

        full_input = self._get_full_input(context)
        
        response = self._call_llm(
            openai_client,
            system_prompt,
            full_input,
            model="gpt-4o-mini",
            max_tokens=400
        )
        
        context.response = response
        context.tool_result = "overwhelm_support_provided"
        
        return context


class PrioritizeTasksHandler(BaseHandler):
    """
    Helps user prioritize when they have too much to do
    
    Logic:
    1. Extract tasks from user's message
    2. Use LLM to categorize by urgency/importance
    3. Present prioritized list
    4. Offer to schedule top priorities
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        # Step 1: Extract tasks from user's message
        tasks = self._extract_tasks(openai_client, context)
        
        if not tasks or len(tasks) == 0:
            # No clear tasks found - offer to help them list things out
            context.response = self._offer_task_listing_help(openai_client, context)
            context.tool_result = None
            return context
        
        # Step 2: Prioritize tasks
        prioritized = self._prioritize_tasks(openai_client, context, tasks)
        
        # Step 3: Generate supportive response with prioritized list
        context.response = self._generate_prioritization_response(
            openai_client, context, prioritized
        )
        context.tool_result = f"Prioritized {len(tasks)} tasks"
        
        return context
    
    def _extract_tasks(self, openai_client: OpenAI, context: ConversationContext) -> List[str]:
        """Extract individual tasks from user's message"""
        full_input = self._get_full_input(context)
        
        prompt = f"""Extract all tasks/to-dos mentioned in this message.

Message: {full_input}

Return ONLY a JSON array of task strings. If no tasks are mentioned, return empty array.

Example: ["finish report", "call dentist", "buy groceries"]

Extract tasks:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200
            )
            
            raw = response.choices[0].message.content
            # Extract JSON array
            match = re.search(r'\[.*?\]', raw, re.DOTALL)
            
            if not match:
                return []
            
            tasks = json.loads(match.group())
            return tasks if isinstance(tasks, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting tasks: {e}")
            return []
    
    def _prioritize_tasks(self, openai_client: OpenAI, context: ConversationContext,
                         tasks: List[str]) -> List[Dict]:
        """Prioritize tasks using Eisenhower Matrix (urgent/important)"""
        
        prompt = f"""Prioritize these tasks using urgency and importance.

Tasks: {json.dumps(tasks)}

For each task, assign:
- priority: "high", "medium", or "low"
- reason: brief explanation (5-10 words)

Return ONLY valid JSON array:
[
  {{"task": "task name", "priority": "high", "reason": "urgent deadline"}},
  ...
]

Prioritize:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300
            )
            
            raw = response.choices[0].message.content
            match = re.search(r'\[.*?\]', raw, re.DOTALL)
            
            if not match:
                # Fallback: return tasks with default priority
                return [{"task": t, "priority": "medium", "reason": "needs attention"} for t in tasks]
            
            prioritized = json.loads(match.group())
            return prioritized
            
        except Exception as e:
            logger.error(f"Error prioritizing tasks: {e}")
            return [{"task": t, "priority": "medium", "reason": "needs attention"} for t in tasks]
    
    def _generate_prioritization_response(self, openai_client: OpenAI,
                                         context: ConversationContext,
                                         prioritized_tasks: List[Dict]) -> str:
        """Generate warm response with prioritized task list"""
        
        # Format task list
        task_list = "\n".join([
            f"• {t['task']} ({t['priority']} priority - {t['reason']})"
            for t in prioritized_tasks
        ])
        
        prompt = f"""You just helped prioritize tasks for someone feeling overwhelmed.

User's emotion: {context.emotion}
Prioritized tasks:
{task_list}

Generate a supportive response that:
1. Acknowledges their situation
2. Presents the prioritized list clearly
3. Suggests starting with just ONE high-priority task
4. Offers reassurance

Tone: Encouraging, practical, warm
Length: 2-3 sentences + the task list

Example format:
"I can see you have a lot on your plate. Here's what I'd suggest tackling first:

• [task] (high priority - [reason])
• [task] (medium priority - [reason])

Start with just the first one. You don't have to do everything today 💙"

Generate response:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=350
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating prioritization response: {e}")
            # Fallback
            return f"Here's how I'd prioritize:\n\n{task_list}\n\nStart with the high-priority items first. One step at a time!"
    
    def _offer_task_listing_help(self, openai_client: OpenAI, context: ConversationContext) -> str:
        """When no tasks are clearly stated, help user articulate them"""
        
        prompt = f"""The user seems overwhelmed but hasn't listed specific tasks yet.

User's message: {context.user_input}
Emotion: {context.emotion}

Generate a gentle prompt to help them list out what's on their mind.

Tone: Supportive, not pushy
Length: 1-2 sentences

Example:
"It sounds like you have a lot going on. Want to tell me what's on your plate? 
Sometimes just listing things out can help."

Generate response:"""

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating task listing prompt: {e}")
            return "Want to tell me what's on your plate? Sometimes just listing things out can help."


class TalkOnlyHandler(BaseHandler):
    """
    Pure emotional support - no action, just listening
    
    Logic:
    1. Validate feelings deeply
    2. Reflect back what they said
    3. Ask gentle follow-up question
    4. NO advice, NO solutions, NO fixing
    
    This is for when user just needs to be heard.
    """
    
    def execute(self, context: ConversationContext, openai_client: OpenAI,
                calendar_service: Any, db_session: Any) -> ConversationContext:
        
        system_prompt = f"""You're a compassionate listener. The user just needs someone to hear them.

User's emotion: {context.emotion}
What they said: {context.user_input}

Your job:
1. VALIDATE - Acknowledge their feelings are valid
2. REFLECT - Show you heard them by reflecting back key points
3. INVITE - Ask a gentle follow-up to let them share more

DO NOT:
- Give advice
- Try to fix anything
- Suggest solutions
- Minimize their feelings

Tone: Deeply empathetic, present, non-judgmental
Length: 2-3 sentences

Example:
"That sounds really hard. It makes sense you'd feel that way given everything you're dealing with. 
Do you want to talk more about it?"

Generate response:"""

        full_input = self._get_full_input(context)
        
        response = self._call_llm(
            openai_client,
            system_prompt,
            full_input,
            model="gpt-4o-mini",
            max_tokens=300
        )
        
        context.response = response
        context.tool_result = "emotional_support_provided"
        
        return context
