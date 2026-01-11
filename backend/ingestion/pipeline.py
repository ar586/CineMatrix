
from datetime import datetime
from backend.datasources.reddit.fetch_posts import RedditFetcher
from backend.datasources.youtube.fetch_videos import YouTubeFetcher
from ml.pipelines.sentiment_worker import SentimentWorker

class DataPipeline:
    def __init__(self):
        self.reddit = RedditFetcher()
        self.youtube = YouTubeFetcher()
        self.worker = SentimentWorker()

    def run_pipeline(self, movie_title: str, movie_id: str):
        """
        Run the ingestion pipeline for a specific movie.
        """
        print(f"Starting ingestion pipeline for: {movie_title} ({movie_id})")
        
        # 1. Fetch Reddit Posts
        print("Fetching Reddit posts...")
        reddit_posts = self.reddit.get_movie_discussions(movie_title, limit=5)
        self._process_list(reddit_posts, "reddit", movie_id)
        
        # 2. Fetch YouTube Videos
        print("Fetching YouTube videos...")
        youtube_videos = self.youtube.search_trailers_and_reviews(movie_title, max_results=5)
        self._process_list(youtube_videos, "youtube", movie_id)
        
        print("Ingestion complete.")

    def _process_list(self, items, source_type, movie_id):
        """
        Process items via SentimentWorker
        """
        for item in items:
            # We explicitly pass the item to the worker. 
            # The worker handles text building, analysis, and DB storage.
            self.worker.process_item(item, source_type, movie_id)
