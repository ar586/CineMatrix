from backend.llm.client import LLMService
import json
import logging

logger = logging.getLogger(__name__)

class DebertaAspect:
    def __init__(self, model_name="llm-fallback"):
        self.llm = LLMService()
        self.aspect_labels = ["acting", "story", "ending", "music", "visuals", "pacing"]

    def extract_aspects(self, text):
        """
        Returns a dictionary of aspect scores using LLM.
        """
        try:
            prompt = f"""
            Analyze the following movie review text and determine the relevance/sentiment of specific aspects.
            Text: "{text}"
            
            Aspects to analyze: {', '.join(self.aspect_labels)}
            
            Return a JSON object where keys are the highly relevant aspects found in the text, and values are a float score (0.0 to 1.0) indicating relevance or sentiment strength.
            Ignore aspects not mentioned.
            
            Example: {{"acting": 0.9, "visuals": 0.8}}
            """
            
            # Use generate_json for safe parsing
            aspects = self.llm.generate_json(prompt)
            
            # Validate format
            valid_aspects = {}
            if isinstance(aspects, dict):
                for k, v in aspects.items():
                    if k in self.aspect_labels and isinstance(v, (int, float)):
                        valid_aspects[k] = float(v)
            
            return valid_aspects

        except Exception as e:
            logger.error(f"Aspect extraction failed: {e}")
            return {}
