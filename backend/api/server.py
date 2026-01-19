from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import sys
import os
import logging
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import backend.config # Load env
from backend.database.client import MongoDBClient
from backend.database.models import Movie, DailyMovieSentiment, Insight, SentimentAnalysis, YouTubeVideo
from backend.datasources.youtube.fetch_videos import YouTubeFetcher

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

from contextlib import asynccontextmanager
from backend.database.deps import get_mongo_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    mongo = get_mongo_client()
    # Provide the db instance to the app state
    # app.state.db = mongo.get_db() # If we wanted to check connection here
    yield
    # Shutdown
    logger.info("Shutting down...")
    if mongo.client:
        mongo.client.close()

app = FastAPI(title="CineMatrix API", version="1.0", lifespan=lifespan)

# Authentication
from backend.auth.router import router as auth_router
app.include_router(auth_router)

# Discussion
from backend.api.discussion import router as discussion_router
app.include_router(discussion_router)

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB connection
# mongo = MongoDBClient()  <-- REMOVE: Do not instantiate global client here
# db = mongo.get_db()      <-- REMOVE

@app.get("/api/health")
def health_check():
    # Helper to check DB status without full dependency chain
    mongo = get_mongo_client()
    db = mongo.get_db()
    return {"status": "ok", "db": "connected" if db is not None else "disconnected"}

@app.get("/api/movies", response_model=List[Movie])
def get_movies():
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Sort: Active first, then by release date (newest first)
    cursor = db.movies.find({}).sort([("is_active", -1), ("release_date", -1)])
    return list(cursor)

@app.put("/api/movies/{movie_id}/status")
def update_movie_status(movie_id: str, is_active: bool = Body(..., embed=True)):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    try:
        query = {"_id": ObjectId(movie_id)}
    except:
        query = {"movie_id": movie_id}
        
    # Check if exists first to handle string IDs reliably
    if not db.movies.find_one(query):
        # Retry with movie_id string if ObjectId failed or didn't match
        query = {"movie_id": movie_id}
        if not db.movies.find_one(query):
             raise HTTPException(404, "Movie not found")
    
    db.movies.update_one(query, {"$set": {"is_active": is_active}})
    return {"status": "updated", "is_active": is_active}

from bson import ObjectId

@app.get("/api/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: str):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    try:
        # Try finding by ObjectId
        movie = db.movies.find_one({"_id": ObjectId(movie_id)})
    except Exception:
        # Fallback to finding by movie_id (tt ID) if ObjectId conversion fails
        movie = db.movies.find_one({"movie_id": movie_id})
        
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    # Normalize IMDB data: populate nested imdb object from flat fields if missing
    if movie.get("imdb") is None and (movie.get("imdb_rating") or movie.get("imdb_votes")):
        movie["imdb"] = {
            "rating": movie.get("imdb_rating"),
            "votes": movie.get("imdb_votes")
        }
    
    return movie

@app.get("/api/movies/{movie_id}/daily", response_model=List[DailyMovieSentiment])
def get_daily_sentiment(movie_id: str):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Fetch last 30 days
    cursor = db.daily_movie_sentiments.find({"movie_id": movie_id}).sort("date", 1).limit(30)
    return list(cursor)

@app.get("/api/movies/{movie_id}/insights", response_model=List[Insight])
def get_insights(movie_id: str):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    cursor = db.insights.find({"movie_id": movie_id}).sort("generated_at", -1).limit(20)
    return list(cursor)

@app.get("/api/movies/{movie_id}/feed")
def get_feed(movie_id: str, limit: int = 50):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Fetch latest raw sentiments
    cursor = db.source_sentiments.find({"movie_id": movie_id}).sort("processed_at", -1).limit(limit)
    raw_items = list(cursor)
    
    # Transform to FeedItem format
    feed_items = []
    for item in raw_items:
        # Extract text from the original discussion (if stored) or use a summary
        text = item.get("text", "")
        if not text:
            # Fallback: create text from sentiment data
            aspects_str = ", ".join([f"{k}: {v}" for k, v in item.get("aspects", {}).items()])
            text = f"Sentiment: {item['sentiment']['label']} ({item['sentiment']['score']}). Aspects: {aspects_str}"
        
        # Extract URL from source_ref
        source_ref = item.get("source_ref", {})
        url = ""
        if item["source"] == "reddit":
            post_id = source_ref.get("post_id", "")
            url = f"https://reddit.com/comments/{post_id}" if post_id else ""
        elif item["source"] == "youtube":
            video_id = source_ref.get("video_id", "")
            url = f"https://youtube.com/watch?v={video_id}" if video_id else ""
        elif item["source"] == "wikipedia":
            url = source_ref.get("url", "")
        elif item["source"] == "imdb":
            url = f"https://www.imdb.com/title/{movie_id}/"
        
        feed_items.append({
            "_id": str(item["_id"]),
            "source": item["source"],
            "text": text,
            "url": url,
            "sentiment": item["sentiment"],
            "created_at": item.get("processed_at", datetime.now()).isoformat()
        })
        
    return feed_items

@app.get("/api/movies/{movie_id}/news")
def get_news(movie_id: str, limit: int = 10):
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Fetch news articles sorted by relevance and date
    cursor = db.news_articles.find({"movie_id": movie_id}).sort([
        ("relevance_score", -1),
        ("fetched_at", -1)
    ]).limit(limit)
    
    articles = list(cursor)
    
    # Transform for frontend
    return [{
        "_id": str(article["_id"]),
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "source": article.get("source", ""),
        "published_date": article.get("fetched_at", datetime.now()).isoformat(),
        "insights": article.get("insights", []),
        "category": article.get("category", "general"),
        "sentiment": article.get("sentiment", "neutral"),
        "relevance_score": article.get("relevance_score", 0.5)
    } for article in articles]


@app.get("/api/movies/{movie_id}/reddit")
def get_reddit_posts(movie_id: str, limit: int = 10):
    """Get Reddit posts and top comments for a movie"""
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Fetch Reddit posts sorted by score (most popular first)
    cursor = db.reddit_posts.find({"movie_id": movie_id}).sort("score", -1).limit(limit)
    posts = list(cursor)
    
    # Transform for frontend - include top 5 comments per post
    reddit_posts = []
    for post in posts:
        # Sort comments by score and take top 5
        comments = sorted(
            post.get("comments", []), 
            key=lambda c: c.get("score", 0), 
            reverse=True
        )[:5]
        
        # Fetch sentiment
        sentiment = db.source_sentiments.find_one({
            "movie_id": movie_id,
            "source": "reddit",
            "source_ref.post_id": post.get("post_id")
        })
        
        reddit_posts.append({
            "_id": str(post["_id"]),
            "post_id": post.get("post_id", ""),
            "subreddit": post.get("subreddit", ""),
            "title": post.get("title", ""),
            "selftext": post.get("selftext", ""),
            "url": post.get("url", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "sentiment": sentiment["sentiment"] if sentiment else None,
            "created_at": post.get("created_at", datetime.now()).isoformat(),
            "comments": [{
                "comment_id": c.get("comment_id", ""),
                "text": c.get("text", ""),
                "score": c.get("score", 0),
                "created_at": c.get("created_at", datetime.now()).isoformat()
            } for c in comments]
        })
    
    return reddit_posts


@app.get("/api/movies/{movie_id}/visualizations")
def get_visualizations(movie_id: str, page: int = 1, limit: int = 5):
    """Get dynamic visualizations generated by LLM-powered agent"""
    try:
        from agents.visualization.viz_agent import VisualizationAgent
        # Pass the global db object directly
        mongo = get_mongo_client()
        db = mongo.get_db()
        logger.info(f"DEBUG: Global db object in server: {db}")
        agent = VisualizationAgent(db=db)
        result = agent.generate_visualizations(movie_id, page, limit)
        return result
    except Exception as e:
        logger.error(f"Visualization generation failed: {e}")
        raise HTTPException(500, f"Failed to generate visualizations: {str(e)}")

@app.get("/api/movies/{movie_id}/youtube", response_model=List[dict])
def get_youtube_videos(movie_id: str):
    """
    Get rich YouTube videos (Trailers + Reviews) with channel info and comments.
    Fetcher is instantiated per request which is okay for now.
    """
    mongo = get_mongo_client()
    db = mongo.get_db()
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Resolve movie title
    try:
        if ObjectId.is_valid(movie_id):
            movie = db.movies.find_one({"_id": ObjectId(movie_id)})
        else:
             movie = db.movies.find_one({"movie_id": movie_id})
    except:
        movie = db.movies.find_one({"movie_id": movie_id})
        
    if not movie:
        raise HTTPException(404, "Movie not found")
        
    title = movie["title"]
    # Use canonical IMDB ID for linking if available
    target_id = movie.get("movie_id", movie_id)
    
    # Fetch from Database (Stored by Agents)
    cursor = db.youtube_videos.find({"movie_id": target_id})
    videos = list(cursor)
    
    # Transform for frontend
    result = []
    for v in videos:
        # Fetch sentiment
        sentiment = db.source_sentiments.find_one({
            "movie_id": target_id,
            "source": "youtube", 
            "source_ref.video_id": v.get("video_id")
        })
        
        result.append({
            "video_id": v.get("video_id"),
            "video_type": v.get("video_type", "review"),
            "title": v.get("title"),
            "channel": v.get("channel"),
            "channel_id": v.get("channel_id"),
            "channel_image": v.get("channel_image"),
            "channel_subs": v.get("channel_subs"),
            "url": v.get("url"),
            "published_at": v.get("published_at"),
            "stats": v.get("stats", {"views": 0, "likes": 0, "comment_count": 0}),
            "sentiment": sentiment["sentiment"] if sentiment else None,
            "comments": v.get("comments", [])
        })
        
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.server:app", host="0.0.0.0", port=8000, reload=True)
