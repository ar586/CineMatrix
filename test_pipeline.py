
from unittest.mock import MagicMock
from backend.ingestion.pipeline import DataPipeline

if __name__ == "__main__":
    # Initialize pipeline
    # We mock fetchers *before* they are used or by patching the class
    # But since DataPipeline inits them in __init__, we likely need to patch the classes or overwrite them instance side.
    # However, RedditClient init fails. So we need to patch the imports.
    
    import sys
    from unittest.mock import Mock
    
    # Mocking modules before import to avoid PRAW init error
    sys.modules['backend.datasources.reddit.fetch_posts'] = Mock()
    sys.modules['backend.datasources.youtube.fetch_videos'] = Mock()
    
    # Now import pipeline (it will use the mocks)
    # BUT pipeline.py imports them at top level. 
    # Actually, pipeline.py does `from backend.datasources.reddit.fetch_posts import RedditFetcher`
    # It might be easier to just mock the instance attributes after creation?
    # No, because `__init__` calls `RedditFetcher()` which calls `RedditClient()` which errors.
    
    # Correct approach: Patching with unittest.mock.patch
    from unittest.mock import patch
    
    with patch('backend.ingestion.pipeline.RedditFetcher') as MockReddit, \
         patch('backend.ingestion.pipeline.YouTubeFetcher') as MockYouTube, \
         patch('backend.ingestion.pipeline.MongoDBClient') as MockDB:
         
        # Setup Mocks
        mock_reddit_instance = MockReddit.return_value
        mock_reddit_instance.get_movie_discussions.return_value = [
            {"id": "post1", "title": "Inception is great", "selftext": "Thinking about it...", "score": 100, "num_comments": 20},
            {"id": "post2", "title": "Confusing text", "selftext": "I hated the end", "score": 0, "num_comments": 5}
        ]
        
        mock_youtube_instance = MockYouTube.return_value
        mock_youtube_instance.search_trailers_and_reviews.return_value = [
            {"id": "vid1", "title": "Inception Review", "description": "Best movie ever", "stats": {"viewCount": "1000", "likeCount": "500"}}
        ]
        
        mock_db_instance = MockDB.return_value
        mock_db_collection = Mock()
        mock_db_instance.get_db.return_value.source_sentiments = mock_db_collection

        print("Initializing Mocked Pipeline...")
        pipeline = DataPipeline()
        
        print("Running Pipeline...")
        pipeline.run_pipeline("Inception", "tt1375666")
        
        # Verify interactions
        print("\n--- Verification ---")
        print(f"Reddit Fetch Called: {mock_reddit_instance.get_movie_discussions.called}")
        print(f"YouTube Fetch Called: {mock_youtube_instance.search_trailers_and_reviews.called}")
        print(f"DB Insertions: {mock_db_collection.insert_one.call_count}")
        
        if mock_db_collection.insert_one.call_count >= 3:
            print("SUCCESS: Pipeline processed and stored items.")
        else:
            print("FAILURE: Pipeline did not store expected items.")
