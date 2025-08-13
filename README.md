                                          Overview
The Emotionally Aware Productivity Assistant is a LangGraph-based AI that blends practical productivity features with empathetic, human-like conversation.
It can:
Detect and respond to your emotional state
Schedule and reschedule events
Set reminders
Summarize conversations
Answer questions & give advice
Handle overwhelm by offering task prioritization or just talking
The assistant adapts its tone and responses dynamically to your mood, making it both a helpful productivity partner and a supportive conversational companion.

                                         Features
Emotion Detection → Routes conversations based on your mood (overwhelm, venting, productive, etc.)
Reminder Management → Extracts what to remind you about and when
Scheduling → Books events via schedule_node
Rescheduling → Adjusts event timings via reschedule_node
Multi-Turn Context → Maintains conversation history (history) for better responses
Tone Adaptation → Uses respond_with_empathy_node to fine-tune messages
Overwhelm Handling → Gives you options: reschedule, prioritize, or talk
Final Response Node → Wraps up interactions in a natural way

                                  Architecture
The assistant is built using:
LangGraph → for defining nodes and routing logic
LLM-powered tools → for extracting event/reminder info and generating empathetic responses
TypedDict state → to store and update user info across nodes

                            Workflow Example
User Input: "I'm feeling overwhelmed, I have too much to do."
respond_with_empathy_node detects emotion → routes to overwhelm_node
post_overwhelm_router_node asks: reschedule tasks, prioritize, or just talk
If "reschedule" → goes to reschedule_node and updates the event list
Ends at final_response_node with a supportive wrap-up

                     Current Limitations
This is an MVP (Minimum Viable Product). Some features are not yet implemented:
Authentication for Scheduling & Rescheduling
Right now, schedule_node and reschedule_node assume open access.
Future: OAuth integration with Google Calendar.

Multi-Intent Routing
Currently routes one action per turn.
Future: Split messages like
"Remind me to call mum and also schedule a meeting."
into multiple actions.

Plugin Expansion
Will add more tools (e.g.knowledge retrieval, document Q&A).

                         Future Roadmap
✅ Emotion-first routing system
✅ Memory for last 4–5 messages
🔄 OAuth calendar integration
🔄 Multi-intent handling
🔄 Plugin store integration
🔄 Better context compression for long conversations

                   How to Run
Install dependencies: pip install -r requirements.txt
Add your .env with: OPENAI_API_KEY=your_key_here

                       Contributing
This is a work in progress — feedback, suggestions, and pull requests are welcome.
The focus is on building a production-ready assistant that’s both practical and human-aware.


