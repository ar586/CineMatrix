import os
import sys
from datetime import datetime, timezone
import logging

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.datasources.reddit.client import RedditClient
from backend.datasources.youtube.client import YouTubeClient
from backend.datasources.imdb.client import IMDBClient
from ml.pipelines.sentiment_engine import SentimentEngine
from backend.aggregation.aggregator import SentimentAggregator
from backend.database.client import MongoDBClient

# Basic Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        # Initialize Components
        self.reddit = RedditClient().get_instance()
        self.youtube = YouTubeClient()
        self.imdb = IMDBClient()
        
        self.engine = SentimentEngine()
        self.aggregator = SentimentAggregator()
        self.db_client = MongoDBClient()

    def process_movie(self, movie_id: str, movie_title: str):
        """
        Run the full agent pipeline for a movie.
        1. Fetch fresh discussions (Reddit/YouTube)
        2. Analyze Sentiment (ML)
        3. Store Results
        4. Aggregate Daily Metrics
        """
        logger.info(f"🎬 Processing Movie: {movie_title} ({movie_id})")
        
        results = []
        
        # --- 1. Gather Signals (Ingestion) ---
        discussions = self._fetch_discussions(movie_title)
        logger.info(f"   Found {len(discussions)} new discussions.")
        
        # --- 2. Reason (Sentiment Analysis) ---
        for disc in discussions:
            try:
                # Analyze text
                res = self.engine.analyze(disc["text"])
                
                # Format for DB (Schema: SentimentAnalysis)
                sentiment_doc = {
                    "movie_id": movie_id,
                    "text": disc["text"],  # Store original text
                    "sentiment": {
                        "label": res.label,
                        "score": res.score,
                        "confidence": res.confidence
                    },
                    "aspects": res.aspects,
                    # "engagement_weight": disc.get("engagement"), # TODO: Add engagement parsing
                    "source": disc["source"],
                    "source_ref": disc.get("source_ref"),
                    "processed_at": datetime.now(timezone.utc)
                }
                results.append(sentiment_doc)
            except Exception as e:
                logger.error(f"   Error analyzing text: {e}")
        
        # --- 3. Store Results ---
        if results:
            db = self.db_client.get_db()
            if db is not None:
                # Batch Insert
                db.source_sentiments.insert_many(results)
                logger.info(f"   ✅ Saved {len(results)} sentiment records.")
            else:
                 logger.error("   ❌ Database connection failed.")
                 return
        
        # --- 4. Aggregate ---
        try:
            daily_stats = self.aggregator.aggregate_daily_sentiment(movie_id, datetime.now(timezone.utc))
            if daily_stats:
                logger.info(f"   ✅ Aggregation Complete. Overall: {daily_stats.overall_sentiment}")
        except Exception as e:
            logger.error(f"   Aggregation Failed: {e}")

    def _fetch_discussions(self, keyword: str):
        """
        Fetch basic discussions from verified sources.
        """
        items = []
        
        # Reddit (Simple search for now)
        try:
            if self.reddit:
                # Searching last 10 posts for the movie
                # Note: Logic can be improved to search specifically by flair or within subreddits
                # For now, searching all reddit.
                search_res = self.reddit.subreddit("all").search(f'"{keyword}"', limit=10, sort="new")
                for post in search_res:
                    items.append({
                        "text": f"{post.title} {post.selftext}",
                        "source": "reddit",
                        "source_ref": {"post_id": post.id},
                        "engagement": {"upvotes": post.score, "comments": post.num_comments}
                    })
        except Exception as e:
            logger.warning(f"Reddit Fetch Error: {e}")

        # YouTube
        try:
            if self.youtube.youtube:
                vid_res = self.youtube.search_videos(keyword, max_results=5)
                # Need to parse response. Assume search_videos returns raw dict
                if vid_res and "items" in vid_res:
                    for item in vid_res["items"]:
                        snippet = item.get("snippet", {})
                        items.append({
                            "text": f"{snippet.get('title')} {snippet.get('description')}",
                            "source": "youtube",
                            "source_ref": {"video_id": item["id"].get("videoId")},
                            "engagement": {} # Need separate call for stats
                        })
        except Exception as e:
             logger.warning(f"YouTube Fetch Error: {e}")
        
        # Wikipedia
        try:
            # Fetch Wikipedia summary for the movie
            wiki_data = self.imdb.fetch_wikipedia_data(keyword)
            if wiki_data:
                items.append({
                    "text": wiki_data.get("summary", ""),
                    "source": "wikipedia",
                    "source_ref": {"url": wiki_data.get("url", "")},
                    "engagement": {}
                })
        except Exception as e:
            logger.warning(f"Wikipedia Fetch Error: {e}")
        
        # IMDB
        try:
            # Fetch IMDB data (reviews, ratings, etc.)
            imdb_data = self.imdb.fetch_movie_data(keyword)
            if imdb_data and imdb_data.get("reviews"):
                for review in imdb_data.get("reviews", [])[:5]:  # Limit to 5 reviews
                    items.append({
                        "text": review.get("text", ""),
                        "source": "imdb",
                        "source_ref": {"review_id": review.get("id", "")},
                        "engagement": {"rating": review.get("rating", 0)}
                    })
        except Exception as e:
            logger.warning(f"IMDB Fetch Error: {e}")
             
        return items

if __name__ == "__main__":
    import backend.config # Ensure env vars loaded
    orch = AgentOrchestrator()
    orch.process_movie("tt1375666", "Inception")
