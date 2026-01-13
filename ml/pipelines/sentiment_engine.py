
import logging
import json
from ml.models.sentiment_model import RobertaSentiment
from ml.models.aspect_model import DebertaAspect
from ml.schemas.source_sentiment import SentimentOutput
from backend.llm.client import LLMService

logger = logging.getLogger(__name__)

class SentimentEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentEngine, cls).__new__(cls)
            cls._instance.sentiment_model = RobertaSentiment()
            cls._instance.aspect_model = DebertaAspect()
            cls._instance.llm = LLMService()
        return cls._instance

    def analyze(self, text: str) -> SentimentOutput:
        # 1. Run Local Models
        label, score, confidence = self.sentiment_model.predict(text)
        aspect_scores = self.aspect_model.extract_aspects(text)
        
        # 2. Refine Aspects (Local heuristic)
        refined_aspects = {}
        for aspect, relevance in aspect_scores.items():
            refined_aspects[aspect] = round(relevance * score, 2)
            
        # 3. Hybrid Refinement (LLM) if low confidence
        if confidence < 0.85:
            logger.info(f"🔍 Low confidence ({confidence:.2f}). Requesting LLM refinement...")
            try:
                prompt = f"""
                Analyze the sentiment of this movie review text.
                
                Text: "{text}"
                
                Local Model Prediction: Label={label}, Score={score:.2f}, Confidence={confidence:.2f}
                
                Task:
                Provide a precise sentiment analysis. 
                - label: 'positive', 'negative', or 'neutral'
                - score: float between -1.0 (neg) and 1.0 (pos)
                - confidence: float between 0.0 and 1.0
                - aspects: Key-value pair of aspect (acting, plot, etc) and its sentiment score (-1 to 1).
                
                Output valid JSON only.
                """
                
                llm_res = self.llm.generate_json(prompt)
                
                if llm_res and "label" in llm_res:
                    label = llm_res.get("label", label)
                    score = float(llm_res.get("score", score))
                    confidence = float(llm_res.get("confidence", confidence))
                    if "aspects" in llm_res:
                         # Merge or override aspects
                         refined_aspects = llm_res["aspects"]
                    logger.info("✅ LLM Refinement applied successfully.")
                    
            except Exception as e:
                logger.warning(f"⚠️ LLM Refinement failed: {e}. Falling back to local model.")

        return SentimentOutput(
            label=label,
            score=round(score, 2),
            confidence=round(confidence, 2),
            aspects=refined_aspects
        )
