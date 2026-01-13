import google.generativeai as genai
import logging
from backend import config
import json

logger = logging.getLogger(__name__)

class LLMService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set. LLM capabilities will be disabled.")
            self.model = None
            return

        genai.configure(api_key=self.api_key)
        self.model_name = getattr(config, "LLM_MODEL", "gemini-1.5-pro-latest")
        
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"✅ LLM Service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM model: {e}")
            self.model = None

    def generate_text(self, prompt: str) -> str:
        """
        Generate free-form text response.
        """
        if not self.model:
            return ""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM Generation Error: {e}")
            return ""

    def generate_json(self, prompt: str, expected_schema: dict = None) -> dict:
        """
        Generate a JSON response. 
        If expected_schema is provided, we can use it to guide the model (if supported) 
        or just append it to the prompt.
        """
        if not self.model:
            return {}

        # Enforce JSON output in prompt
        json_prompt = f"{prompt}\n\nIMPORTANT: Output strictly valid JSON. No markdown backticks."
        
        try:
            response = self.model.generate_content(json_prompt)
            text = response.text
            
            # Clean up potential markdown formatting
            text = text.replace("```json", "").replace("```", "").strip()
            
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error(f"LLM failed to return valid JSON: {text}")
            return {}
        except Exception as e:
            logger.error(f"LLM JSON Generation Error: {e}")
            return {}

if __name__ == "__main__":
    # Test
    llm = LLMService()
    print(llm.generate_text("Say hello to CineMatrix developers!"))
