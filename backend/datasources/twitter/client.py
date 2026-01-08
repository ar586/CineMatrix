
from openai import OpenAI
import os

class GrokClient:
    def __init__(self):
        """
        Initialize Grok (xAI) Client using OpenAI SDK.
        Expects 'XAI_API_KEY' in environment variables.
        """
        self.api_key = os.getenv("XAI_API_KEY")
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )
        else:
            self.client = None

    def chat_completion(self, messages, model="grok-beta"):
        """
        Send a chat completion request to Grok.
        """
        if not self.client:
            raise ValueError("XAI_API_KEY not found.")

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Grok API Error: {e}")
            return None
