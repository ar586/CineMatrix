
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

    def analyze(self, text: str, source: str = "unknown", metadata: dict = None) -> SentimentOutput:
        if metadata is None:
            metadata = {}
            
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
                metadata_str = json.dumps(metadata, indent=2, default=str)
                prompt = f"""
                You are an advanced sentiment analysis engine for movie market intelligence.
                You are analyzing content from {source}.

                Context & Metadata:
                - Source Type: {source} (e.g., reddit, youtube, twitter)
                - Engagement/Metadata: {metadata_str}

                **Guidance on Media Forms & Engagement:**
                1. **YouTube**:
                   - **Transcripts**: Represents the content of the video itself.
                   - **Comments**: User reactions. HIGH 'like' counts on comments indicate strong community agreement with that sentiment.
                2. **Reddit**:
                   - **Submissions (Main Post)**: The primary opinion/review.
                   - **Comments**: Discussion. IMPORTANT: Pay attention to 'upvotes'. A highly upvoted comment (high positive score) implies the sentiment is widely shared and validated by the community.
                3. **General**:
                   - High engagement (likes, upvotes, retweets) amplifies the significance of the sentiment. A negative review with 10k likes is far more improving than one with 0 likes.

                Text to Analyze:
                "{text}"
                
                Local Model Prediction (Reference):
                Label={label}, Score={score:.2f}, Confidence={confidence:.2f}
                
                Task:
                Analyze the sentiment of the text, taking into account the source context and engagement signals.
                Provide a structured analysis: 
                - **label**: 'positive', 'negative', or 'neutral'
                - **score**: float between -1.0 (neg) and 1.0 (pos)
                - **confidence**: float between 0.0 and 1.0 (if the text is sarcastic but has high upvotes, you might infer the true sentiment is the opposite of the literal text, or simply that the sarcasm is agreed upon).
                - **aspects**: Key-value pair of aspect (acting, plot, visual, etc) and its sentiment score (-1 to 1).
                
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
