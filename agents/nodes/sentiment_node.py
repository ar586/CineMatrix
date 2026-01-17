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
        
        # Filter out similar signals using similarity detection
        db = self.db_client.get_db()
        if db is not None:
            from backend.database.similarity import text_similarity
            
            # Get existing texts for this movie
            existing_sentiments = db.source_sentiments.find(
                {"movie_id": movie_id},
                {"text": 1}
            ).limit(200)
            existing_texts = [s.get("text", "") for s in existing_sentiments]
            
            # Filter signals
            filtered_signals = []
            for signal in signals:
                signal_text = signal.get("text", "")
                is_duplicate = False
                
                # Check similarity against existing texts
                for existing_text in existing_texts:
                    if text_similarity(signal_text[:500], existing_text[:500]) >= 0.85:
                        logger.info(f"   ⏭️  Skipping similar signal from {signal['source']}")
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    filtered_signals.append(signal)
            
            logger.info(f"   Filtered {len(signals)} signals → {len(filtered_signals)} unique signals")
            signals = filtered_signals
        
        results = []
        for signal in signals:
            try:
                # Analyze text
                res = self.engine.analyze(
                    text=signal["text"],
                    source=signal.get("source", "unknown"),
                    metadata=signal.get("metadata", {})
                )
                
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
                # Use bulk upsert to prevent duplicates
                from backend.database.dedup import bulk_upsert_sentiments
                bulk_upsert_sentiments(db, results)
                logger.info(f"   ✅ Saved {len(results)} sentiment records (with deduplication).")
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
