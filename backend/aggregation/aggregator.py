
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from backend.database.client import MongoDBClient
from backend.database.models import DailyMovieSentiment, SourceBreakdown, Volume, Aspects

class SentimentAggregator:
    def __init__(self):
        self.db_client = MongoDBClient()

    def aggregate_daily_sentiment(self, movie_id: str, date: datetime):
        """
        Aggregates sentiment for a specific movie and date.
        Date is expected to be a datetime object (will filter for that entire day UTC).
        """
        db = self.db_client.get_db()
        collection = db.source_sentiments
        
        # Define time range for the given date (00:00:00 to 23:59:59)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = {
            "movie_id": movie_id,
            "processed_at": {
                "$gte": start_of_day,
                "$lt": end_of_day
            }
        }
        
        cursor = collection.find(query)
        items = list(cursor)
        
        if not items:
            print(f"No sentiment data found for {movie_id} on {date.date()}")
            return None

        # --- Metrics Calculation ---
        
        # 1. Overall Sentiment (Simple average for MVP, could be weighted by confidence/engagement)
        sentiment_scores = [item["sentiment"]["score"] for item in items]
        overall_sentiment = float(np.mean(sentiment_scores))
        
        # 2. Volatility (Standard Deviation)
        volatility = float(np.std(sentiment_scores)) if len(sentiment_scores) > 1 else 0.0
        
        # 3. Confidence (Average confidence)
        confidence_scores = [item["sentiment"]["confidence"] for item in items]
        avg_confidence = float(np.mean(confidence_scores))
        
        # 4. Source Breakdown & Volume
        source_scores = {"reddit": [], "youtube": []}
        source_counts = {"reddit": 0, "youtube": 0}
        
        for item in items:
            source = item["source"]
            score = item["sentiment"]["score"]
            
            if source in source_scores:
                source_scores[source].append(score)
                source_counts[source] += 1
            else:
                # Handle unknown sources dynamically if needed, skipping for fixed schema now
                pass
                
        source_breakdown_dict = {}
        for source, scores in source_scores.items():
            if scores:
                source_breakdown_dict[source] = float(np.mean(scores))
            else:
                source_breakdown_dict[source] = None

        # 5. Aspect Summary
        # Collect all aspect scores
        aspect_totals: Dict[str, List[float]] = {}
        
        for item in items:
            aspects = item.get("aspects", {})
            if aspects:
                for key, val in aspects.items():
                    if key not in aspect_totals:
                        aspect_totals[key] = []
                    aspect_totals[key].append(val)
        
        aspect_summary_dict = {}
        for key, vals in aspect_totals.items():
            aspect_summary_dict[key] = float(np.mean(vals))

        # --- Construct DB Object ---
        
        daily_sentiment = DailyMovieSentiment(
            movie_id=movie_id,
            date=date.strftime("%Y-%m-%d"),
            overall_sentiment=round(overall_sentiment, 2),
            confidence=round(avg_confidence, 2),
            source_breakdown=SourceBreakdown(**source_breakdown_dict),
            aspect_summary=Aspects(**aspect_summary_dict), # Pydantic extra="allow" handles dynamic keys
            volume=Volume(
                reddit_posts=source_counts["reddit"], 
                youtube_videos=source_counts["youtube"]
            ),
            volatility=round(volatility, 2),
            created_at=datetime.utcnow()
        )
        
        # Insert or Update
        target_collection = db.daily_movie_sentiments
        # Upsert based on movie_id and date
        target_collection.update_one(
            {"movie_id": movie_id, "date": date.strftime("%Y-%m-%d")},
            {"$set": daily_sentiment.model_dump(by_alias=True)},
            upsert=True
        )
        
        print(f"Aggregated sentiment for {movie_id} on {date.date()}: {overall_sentiment}")
        return daily_sentiment

if __name__ == "__main__":
    # Example usage
    agg = SentimentAggregator()
    # agg.aggregate_daily_sentiment("tt1375666", datetime.now())
