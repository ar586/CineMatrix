
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
import numpy as np
import sys

# Mocking numpy just in case, though standard lib is fine. Actually numpy is used.
# But we can let it run real numpy if installed. 
# `test_pipeline` failed on PRAW, so we need to mock DB client.

from backend.aggregation.aggregator import SentimentAggregator

class TestAggregation(unittest.TestCase):
    
    @patch("backend.aggregation.aggregator.MongoDBClient")
    def test_aggregate_daily(self, MockDB):
        # Setup Mock DB Data
        mock_db = MockDB.return_value.get_db.return_value
        mock_source_collection = mock_db.source_sentiments
        mock_daily_collection = mock_db.daily_movie_sentiments
        
        # Create dummy sentiment items
        base_time = datetime(2026, 1, 10, 12, 0, 0)
        items = [
            {
                "movie_id": "tt1",
                "source": "reddit",
                "sentiment": {"score": 0.8, "confidence": 0.9},
                "aspects": {"acting": 0.9, "story": 0.5},
                "processed_at": base_time
            },
            {
                "movie_id": "tt1",
                "source": "reddit",
                "sentiment": {"score": 0.6, "confidence": 0.8},
                "aspects": {"acting": 0.7, "story": 0.6},
                "processed_at": base_time
            },
            {
                "movie_id": "tt1",
                "source": "youtube",
                "sentiment": {"score": -0.2, "confidence": 0.95},
                "aspects": {"visuals": 0.9},
                "processed_at": base_time
            }
        ]
        
        # Mock find return
        mock_source_collection.find.return_value = items
        
        aggregator = SentimentAggregator()
        result = aggregator.aggregate_daily_sentiment("tt1", datetime(2026, 1, 10))
        
        print("\n--- Aggregation Result ---")
        print(f"Overall Sentiment: {result.overall_sentiment}")
        print(f"Volatility: {result.volatility}")
        print(f"Reddit Volume: {result.volume.reddit_posts}")
        print(f"Acting Aspect: {result.aspect_summary.acting}")
        
        # Validations
        # Scores: 0.8, 0.6, -0.2 -> Avg = 0.4
        self.assertAlmostEqual(result.overall_sentiment, 0.4)
        
        # Aspects: Acting (0.9, 0.7) -> 0.8
        self.assertAlmostEqual(result.aspect_summary.acting, 0.8)
        
        # Volume
        self.assertEqual(result.volume.reddit_posts, 2)
        self.assertEqual(result.volume.youtube_videos, 1)
        
        # Verify DB Update called
        self.assertTrue(mock_daily_collection.update_one.called)

if __name__ == "__main__":
    unittest.main()
