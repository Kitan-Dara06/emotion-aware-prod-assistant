from emotion_aware_assistant.gloabal_import import *
from emotion_aware_assistant.services.llm_model import llm
def parse_json_output(ai_msg):
    try:
        # Check if it's an AIMessage (LangChain), else treat as raw string
        raw_text = ai_msg.content if hasattr(ai_msg, "content") else str(ai_msg)

        matches = re.findall(r"\{.*?\}", raw_text, re.DOTALL)

        for json_str in matches:
            try:
                parsed = json.loads(json_str)
                if all(k in parsed for k in ["emotion", "goal", "suggested_action", ]):
                    return parsed
            except json.JSONDecodeError:
                continue  # Try next one if not valid JSON

        raise ValueError("No valid JSON object with required keys found.")

    except Exception as e:
        return {
            "error": str(e),
            "raw_output": str(ai_msg)[:1000]
        }

def Reminder(full_input):
    messages = [
        SystemMessage(content="""
You are a JSON extraction tool.

Extract a reminder from the user's input.

Return ONLY a valid JSON object. No explanation. No extra text.

Required keys:
- "reminder": what to do
- "time": when to do it

Example:
{
  "reminder": "buy groceries",
  "time": "5pm"
}
"""),
        HumanMessage(content=full_input)
    ]

    try:
        print("Sending request to LLM...")
        response = llm.invoke(messages, config={"max_tokens": 80, "temperature": 0})
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        output_text = getattr(response, 'content', None) or str(response)
        print(f"Extracted text: {output_text}")

    except Exception as e:
        print(f"Error during API call: {str(e)}")
        return {"error": str(e)}

    # Try to extract a valid JSON from the model's output
    match = re.search(r"\{[\s\S]+?\}", output_text)
    if match:
        try:
            result = json.loads(match.group())
              # Basic validation
            if "reminder" not in result or not result["reminder"]:
                return {"error": "Missing reminder text", "raw_output": output_text}
            if "time" not in result or not result["time"]:
                return {"error": "Can you be more specific about when?"}

            return result

        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}", "raw_output": output_text}
    else:
        return {"error": "No JSON found", "raw_output": output_text}
