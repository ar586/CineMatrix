#!/usr/bin/env python3
"""
Create unique indexes for deduplication across all collections.
Run this script before updating nodes to prevent duplicate key errors.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient

def create_dedup_indexes():
    """Create unique compound indexes for all collections"""
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    print("Creating deduplication indexes...")
    
    # Reddit posts: unique per movie + post_id
    print("  - reddit_posts: (movie_id, post_id)")
    db.reddit_posts.create_index(
        [("movie_id", 1), ("post_id", 1)], 
        unique=True,
        name="unique_movie_post"
    )
    
    # YouTube videos: unique per movie + video_id
    print("  - youtube_videos: (movie_id, video_id)")
    db.youtube_videos.create_index(
        [("movie_id", 1), ("video_id", 1)], 
        unique=True,
        name="unique_movie_video"
    )
    
    # News articles: unique per movie + URL
    print("  - news_articles: (movie_id, url)")
    db.news_articles.create_index(
        [("movie_id", 1), ("url", 1)], 
        unique=True,
        name="unique_movie_article"
    )
    
    # Sentiment analysis: unique per movie + source + source_ref
    # Using sparse index since source_ref fields may not always exist
    print("  - source_sentiments: (movie_id, source, source_ref)")
    db.source_sentiments.create_index(
        [
            ("movie_id", 1), 
            ("source", 1),
            ("source_ref.post_id", 1),
            ("source_ref.video_id", 1)
        ], 
        unique=True,
        sparse=True,
        name="unique_movie_source_sentiment"
    )
    
    # Google Trends: unique per movie + region + date
    print("  - google_trends: (movie_id, region, date)")
    db.google_trends.create_index(
        [("movie_id", 1), ("region", 1), ("date", 1)], 
        unique=True,
        name="unique_movie_region_date"
    )
    
    # Movie Events: unique per movie + type + date
    print("  - movie_events: (movie_id, event_type, event_date)")
    db.movie_events.create_index(
        [("movie_id", 1), ("event_type", 1), ("event_date", 1)], 
        unique=True,
        name="unique_movie_event"
    )
    
    print("\n✅ All deduplication indexes created successfully!")
    print("\nNote: If you see 'duplicate key' errors when running the pipeline,")
    print("it means duplicates already exist. You may need to clean them first.")

if __name__ == "__main__":
    try:
        create_dedup_indexes()
    except Exception as e:
        print(f"\n❌ Error creating indexes: {e}")
        sys.exit(1)
