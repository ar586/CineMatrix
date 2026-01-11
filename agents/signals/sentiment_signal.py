
from backend.ml.sentiment_model import RobertaSentiment
from backend.ml.aspect_model import DebertaAspect

class SentimentSignal:
    def __init__(self):
        # Initializing models here might be slow on each instantiation.
        # Ideally, use a Singleton or pass them in dependency injection.
        # For now, we load them lazily or here.
        self.sentiment_model = RobertaSentiment()
        self.aspect_model = DebertaAspect()

    def analyze(self, text: str, source: str, source_ref: dict) -> dict:
        """
        Analyze sentiment from text data.
        Returns a dict matching the SentimentAnalysis schema input.
        """
        # Run Roberta Model
        label, score, confidence = self.sentiment_model.predict(text)
        
        # Run Aspect Extraction (Zero-Shot)
        aspect_scores = self.aspect_model.extract_aspects(text)
        
        # Refine aspect scores based on overall sentiment
        # Currently DebertaAspect returns "relevance". 
        # We multiply by the overall polarity score to estimate "aspect sentiment".
        # e.g., if Overall Score = -0.8 and Acting Relevance = 0.9 -> Acting = -0.72
        refined_aspects = {}
        for aspect, relevance in aspect_scores.items():
            refined_aspects[aspect] = round(relevance * score, 2)
            
        return {
            "sentiment": {
                "label": label,
                "score": round(score, 2),
                "confidence": round(confidence, 2)
            },
            "aspects": refined_aspects
        }
