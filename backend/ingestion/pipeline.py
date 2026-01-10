
from datetime import datetime
from backend.datasources.reddit.fetch_posts import RedditFetcher
from backend.datasources.youtube.fetch_videos import YouTubeFetcher
from agents.signals.sentiment_signal import SentimentSignal
from backend.database.client import MongoDBClient
from backend.database.models import SentimentAnalysis, SourceRef

class DataPipeline:
    def __init__(self):
        self.reddit = RedditFetcher()
        self.youtube = YouTubeFetcher()
        self.sentiment_agent = SentimentSignal()
        self.db_client = MongoDBClient()

    def run_pipeline(self, movie_title: str, movie_id: str):
        """
        Run the ingestion pipeline for a specific movie.
        """
        print(f"Starting ingestion pipeline for: {movie_title} ({movie_id})")
        
        # 1. Fetch Reddit Posts
        print("Fetching Reddit posts...")
        reddit_posts = self.reddit.get_movie_discussions(movie_title, limit=5)
        self._process_and_store(reddit_posts, "reddit", movie_id)
        
        # 2. Fetch YouTube Videos
        print("Fetching YouTube videos...")
        youtube_videos = self.youtube.search_trailers_and_reviews(movie_title, max_results=5)
        self._process_and_store(youtube_videos, "youtube", movie_id)
        
        print("Ingestion complete.")

    def _process_and_store(self, items, source_type, movie_id):
        """
        Process items via Sentiment Agent and store in MongoDB.
        """
        db = self.db_client.get_db()
        collection = db.source_sentiments
        
        for item in items:
            text_content = ""
            source_ref = {}
            engagement = {}
            
            if source_type == "reddit":
                text_content = f"{item.get('title', '')} {item.get('selftext', '')}"
                source_ref = {"post_id": item.get("id")}
                engagement = {
                    "upvotes": item.get("score"),
                    "comment_count": item.get("num_comments")
                }
            elif source_type == "youtube":
                text_content = f"{item.get('title', '')} {item.get('description', '')}"
                source_ref = {"video_id": item.get("id")}
                # Stats might be nested or direct depending on parser, assuming generic structure for now
                stats = item.get("stats", {})
                engagement = {
                    "views": int(stats.get("viewCount", 0)) if stats.get("viewCount") else 0,
                    "likes": int(stats.get("likeCount", 0)) if stats.get("likeCount") else 0
                }

            # Analyze Sentiment
            analysis = self.sentiment_agent.analyze(text_content, source_type, source_ref)
            
            # Construct SentimentAnalysis Object
            model_data = {
                "movie_id": movie_id,
                "source": source_type,
                "source_ref": source_ref,
                "sentiment": analysis["sentiment"],
                "aspects": analysis["aspects"],
                "engagement_weight": engagement,
                "model": {
                    "name": "basic-heuristic",
                    "version": "0.1",
                    "aggregation": "text_only"
                },
                "processed_at": datetime.utcnow()
            }
            
            try:
                # Valiate with Pydantic
                sa_obj = SentimentAnalysis(**model_data)
                # Store in DB
                collection.insert_one(sa_obj.model_dump(by_alias=True))
                print(f"Stored sentiment for {source_type} item.")
            except Exception as e:
                print(f"Failed to store item: {e}")
