
from backend.llm.client import LLMService

class RobertaSentiment:
    def __init__(self, model_name="llm-fallback"):
        self.llm = LLMService()
        self.labels = ["negative", "neutral", "positive"]

    def predict(self, text):
        """
        Returns label, score, and confidence using LLM.
        """
        try:
            prompt = f"""
            Analyze the sentiment of this text.
            Text: "{text}"
            
            Return JSON with:
            - label: 'positive', 'negative', or 'neutral'
            - score: float between -1.0 (negative) and 1.0 (positive)
            - confidence: float between 0.0 and 1.0 indicating how sure you are.
            """
            
            result = self.llm.generate_json(prompt)
            
            label = result.get("label", "neutral")
            score = float(result.get("score", 0.0))
            confidence = float(result.get("confidence", 0.5))
            
            if label not in self.labels:
                label = "neutral"
                
            return label, score, confidence

        except Exception as e:
            print(f"Error in LLM Sentiment: {e}")
            return "neutral", 0.0, 0.0
