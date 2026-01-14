import logging
from datetime import datetime, timezone
from agents.state import AgentState
from ml.pipelines.sentiment_engine import SentimentEngine
from backend.database.client import MongoDBClient
from backend.aggregation.aggregator import SentimentAggregator

logger = logging.getLogger(__name__)

class SentimentNode:
    def __init__(self):
        self.engine = SentimentEngine()
        self.db_client = MongoDBClient()
        self.aggregator = SentimentAggregator()
    
    def __call__(self, state: AgentState):
        logger.info("🧠 [Sentiment Node] Analyzing signals...")
        signals = state.get("signals", [])
        movie_id = state["movie_id"]
        
        results = []
        for signal in signals:
            try:
                # Analyze text
                res = self.engine.analyze(signal["text"])
                
                # Format for DB (Schema: SentimentAnalysis)
                sentiment_doc = {
                    "movie_id": movie_id,
                    "text": signal["text"],
                    "sentiment": {
                        "label": res.label,
                        "score": res.score,
                        "confidence": res.confidence
                    },
                    "aspects": res.aspects,
                    "source": signal["source"],
                    "source_ref": signal.get("metadata", {}),
                    "url": signal.get("url"),
                    "processed_at": datetime.now(timezone.utc)
                }
                results.append(sentiment_doc)
            except Exception as e:
                logger.error(f"   Error analyzing text from {signal['source']}: {e}")
        
        # Store Results
        if results:
            db = self.db_client.get_db()
            if db is not None:
                db.source_sentiments.insert_many(results)
                logger.info(f"   ✅ Saved {len(results)} sentiment records.")
            else:
                logger.error("   ❌ Database connection failed.")
                return {"errors": ["Database connection failed"]}
        
        # Aggregate
        try:
            daily_stats = self.aggregator.aggregate_daily_sentiment(movie_id, datetime.now(timezone.utc))
            if daily_stats:
                logger.info(f"   ✅ Aggregation Complete.")
        except Exception as e:
            logger.error(f"   Aggregation Failed: {e}")

        return {"signals": []} # Clear signals after processing if needed, or pass them through
