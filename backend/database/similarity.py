"""
Similarity-based deduplication to catch near-duplicates.
Uses text similarity matching to identify cross-posts, syndicated articles, etc.
"""

from difflib import SequenceMatcher
from typing import Optional, List, Dict, Any

def text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity ratio between two texts (0-1).
    Uses SequenceMatcher for fast approximate matching.
    
    Args:
        text1: First text to compare
        text2: Second text to compare
        
    Returns:
        Similarity ratio between 0.0 (completely different) and 1.0 (identical)
    """
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def find_similar_reddit_post(db, movie_id: str, title: str, threshold: float = 0.85) -> Optional[str]:
    """
    Check if a similar Reddit post already exists for this movie.
    
    Args:
        db: MongoDB database instance
        movie_id: Movie ID to search within
        title: Post title to compare
        threshold: Similarity threshold (0.0-1.0), default 0.85
        
    Returns:
        post_id of similar post if found, None otherwise
    """
    existing_posts = db.reddit_posts.find(
        {"movie_id": movie_id},
        {"title": 1, "post_id": 1}
    ).limit(100)  # Limit to recent posts for performance
    
    for post in existing_posts:
        similarity = text_similarity(title, post.get("title", ""))
        if similarity >= threshold:
            return post["post_id"]
    
    return None

def find_similar_news_article(db, movie_id: str, title: str, threshold: float = 0.90) -> Optional[str]:
    """
    Check if a similar news article already exists for this movie.
    Uses higher threshold (0.90) since news titles are more standardized.
    
    Args:
        db: MongoDB database instance
        movie_id: Movie ID to search within
        title: Article title to compare
        threshold: Similarity threshold (0.0-1.0), default 0.90
        
    Returns:
        url of similar article if found, None otherwise
    """
    existing_articles = db.news_articles.find(
        {"movie_id": movie_id},
        {"title": 1, "url": 1}
    ).limit(100)  # Limit for performance
    
    for article in existing_articles:
        similarity = text_similarity(title, article.get("title", ""))
        if similarity >= threshold:
            return article["url"]
    
    return None

def find_similar_youtube_video(db, movie_id: str, title: str, threshold: float = 0.85) -> Optional[str]:
    """
    Check if a similar YouTube video already exists for this movie.
    
    Args:
        db: MongoDB database instance
        movie_id: Movie ID to search within
        title: Video title to compare
        threshold: Similarity threshold (0.0-1.0), default 0.85
        
    Returns:
        video_id of similar video if found, None otherwise
    """
    existing_videos = db.youtube_videos.find(
        {"movie_id": movie_id},
        {"title": 1, "video_id": 1}
    ).limit(100)
    
    for video in existing_videos:
        similarity = text_similarity(title, video.get("title", ""))
        if similarity >= threshold:
            return video["video_id"]
    
    return None

def filter_similar_items(
    db, 
    movie_id: str, 
    items: List[Dict[str, Any]], 
    collection_name: str,
    title_key: str = "title",
    threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """
    Generic function to filter out similar items from a list.
    
    Args:
        db: MongoDB database instance
        movie_id: Movie ID to search within
        items: List of items to filter
        collection_name: Name of collection to check against
        title_key: Key in item dict that contains the title/text to compare
        threshold: Similarity threshold
        
    Returns:
        Filtered list with similar items removed
    """
    if not items:
        return []
    
    # Get existing titles from database
    existing = db[collection_name].find(
        {"movie_id": movie_id},
        {title_key: 1}
    ).limit(200)
    
    existing_titles = [doc.get(title_key, "") for doc in existing]
    
    # Filter items
    filtered = []
    for item in items:
        item_title = item.get(title_key, "")
        is_duplicate = False
        
        for existing_title in existing_titles:
            if text_similarity(item_title, existing_title) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered.append(item)
    
    return filtered

def batch_check_similarity(
    titles: List[str], 
    existing_titles: List[str], 
    threshold: float = 0.85
) -> List[bool]:
    """
    Batch check if titles are similar to existing titles.
    More efficient than checking one by one.
    
    Args:
        titles: List of titles to check
        existing_titles: List of existing titles to compare against
        threshold: Similarity threshold
        
    Returns:
        List of booleans indicating if each title is a duplicate
    """
    results = []
    
    for title in titles:
        is_duplicate = False
        for existing in existing_titles:
            if text_similarity(title, existing) >= threshold:
                is_duplicate = True
                break
        results.append(is_duplicate)
    
    return results
