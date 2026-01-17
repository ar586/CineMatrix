"""
Deduplication utilities for preventing duplicate data in the pipeline.
Provides upsert operations for all major data sources.
"""

from pymongo.operations import UpdateOne
from typing import List, Dict, Any

def upsert_reddit_post(db, post_data: Dict[str, Any]):
    """
    Insert or update Reddit post, avoiding duplicates.
    Uses movie_id + post_id as unique key.
    """
    return db.reddit_posts.update_one(
        {
            "movie_id": post_data["movie_id"], 
            "post_id": post_data["post_id"]
        },
        {"$set": post_data},
        upsert=True
    )

def upsert_youtube_video(db, video_data: Dict[str, Any]):
    """
    Insert or update YouTube video, avoiding duplicates.
    Uses movie_id + video_id as unique key.
    """
    return db.youtube_videos.update_one(
        {
            "movie_id": video_data["movie_id"], 
            "video_id": video_data["video_id"]
        },
        {"$set": video_data},
        upsert=True
    )

def upsert_news_article(db, article_data: Dict[str, Any]):
    """
    Insert or update news article, avoiding duplicates.
    Uses movie_id + url as unique key.
    """
    return db.news_articles.update_one(
        {
            "movie_id": article_data["movie_id"], 
            "url": article_data["url"]
        },
        {"$set": article_data},
        upsert=True
    )

def bulk_upsert_sentiments(db, sentiments: List[Dict[str, Any]]):
    """
    Bulk upsert sentiment analyses, avoiding duplicates.
    Uses movie_id + source + source_ref as unique key.
    """
    if not sentiments:
        return None
        
    operations = []
    for s in sentiments:
        # Safety: Remove _id if it exists
        if "_id" in s:
            del s["_id"]
            
        with open("/Users/mac/Desktop/CineMatrix/debug_sentiments.log", "a") as f:
            import json
            try:
                f.write(json.dumps(s, default=str) + "\n")
            except:
                f.write(f"Could not dump s: {s}\n")

        operations.append(
            UpdateOne(
                {
                    "movie_id": s["movie_id"],
                    "source": s["source"],
                    "source_ref": s.get("source_ref", {})
                },
                {"$set": s},
                upsert=True
            )
        )
    
    return db.source_sentiments.bulk_write(operations)

def bulk_upsert_reddit_posts(db, posts: List[Dict[str, Any]]):
    """
    Bulk upsert Reddit posts for better performance.
    """
    if not posts:
        return None
        
    operations = []
    for post in posts:
        operations.append(
            UpdateOne(
                {
                    "movie_id": post["movie_id"],
                    "post_id": post["post_id"]
                },
                {"$set": post},
                upsert=True
            )
        )
    
    return db.reddit_posts.bulk_write(operations)

def bulk_upsert_youtube_videos(db, videos: List[Dict[str, Any]]):
    """
    Bulk upsert YouTube videos for better performance.
    """
    if not videos:
        return None
        
    operations = []
    for video in videos:
        operations.append(
            UpdateOne(
                {
                    "movie_id": video["movie_id"],
                    "video_id": video["video_id"]
                },
                {"$set": video},
                upsert=True
            )
        )
    
    return db.youtube_videos.bulk_write(operations)

def bulk_upsert_news_articles(db, articles: List[Dict[str, Any]]):
    """
    Bulk upsert news articles for better performance.
    """
    if not articles:
        return None
        
    operations = []
    for article in articles:
        operations.append(
            UpdateOne(
                {
                    "movie_id": article["movie_id"],
                    "url": article["url"]
                },
                {"$set": article},
                upsert=True
            )
        )
    
    return db.news_articles.bulk_write(operations)

def get_existing_reddit_post_ids(db, movie_id: str) -> set:
    """
    Get set of already-fetched Reddit post IDs for a movie.
    Useful for filtering before fetching.
    """
    existing = db.reddit_posts.find(
        {"movie_id": movie_id},
        {"post_id": 1}
    )
    return {post["post_id"] for post in existing}

def get_existing_youtube_video_ids(db, movie_id: str) -> set:
    """
    Get set of already-fetched YouTube video IDs for a movie.
    Useful for filtering before fetching.
    """
    existing = db.youtube_videos.find(
        {"movie_id": movie_id},
        {"video_id": 1}
    )
    return {video["video_id"] for video in existing}

def get_existing_news_urls(db, movie_id: str) -> set:
    """
    Get set of already-fetched news article URLs for a movie.
    Useful for filtering before fetching.
    """
    existing = db.news_articles.find(
        {"movie_id": movie_id},
        {"url": 1}
    )
    return {article["url"] for article in existing}
