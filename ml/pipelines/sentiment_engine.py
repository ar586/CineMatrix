
from ml.models.sentiment_model import RobertaSentiment
from ml.models.aspect_model import DebertaAspect
from ml.schemas.source_sentiment import SentimentOutput

class SentimentEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentEngine, cls).__new__(cls)
            cls._instance.sentiment_model = RobertaSentiment()
            cls._instance.aspect_model = DebertaAspect()
        return cls._instance

    def analyze(self, text: str) -> SentimentOutput:
        # Run Roberta
        label, score, confidence = self.sentiment_model.predict(text)
        
        # Run Deberta
        aspect_scores = self.aspect_model.extract_aspects(text)
        
        # Refine aspects
        refined_aspects = {}
        for aspect, relevance in aspect_scores.items():
            refined_aspects[aspect] = round(relevance * score, 2)
            
        return SentimentOutput(
            label=label,
            score=round(score, 2),
            confidence=round(confidence, 2),
            aspects=refined_aspects
        )
