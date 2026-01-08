
import json
import re

class GrokParser:
    def parse_response(self, response_text):
        """
        Parse the text response from Grok into a dictionary.
        Handles Markdown code blocks.
        """
        if not response_text:
            return None

        try:
            # 1. Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 2. Try extracting from ```json ... ``` or ``` ... ```
            match = re.search(r"```(?:json)?\s*(.*?)```", response_text, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # 3. Fallback: Return raw text wrapped in a dict
            return {"raw_summary": response_text}
