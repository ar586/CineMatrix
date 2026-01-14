from fastapi import FastAPI, HTTPException
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
from backend.database.models import Movie, DailyMovieSentiment, Insight, SentimentAnalysis

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(title="CineMatrix API", version="1.0")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB connection
mongo = MongoDBClient()
db = mongo.get_db()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "connected" if db is not None else "disconnected"}

@app.get("/api/movies", response_model=List[Movie])
def get_movies(active_only: bool = True):
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    query = {"is_active": True} if active_only else {}
    movies = list(db.movies.find(query))
    
    # Sort by 'heat' (volatility or volume) if available? 
    # For now, just return all.
    return movies

@app.get("/api/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: str):
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    movie = db.movies.find_one({"_id": movie_id})
    if not movie:
        raise HTTPException(404, "Movie not found")
    return movie

@app.get("/api/movies/{movie_id}/daily", response_model=List[DailyMovieSentiment])
def get_daily_sentiment(movie_id: str):
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    # Fetch last 30 days
    cursor = db.daily_sentiments.find({"movie_id": movie_id}).sort("date", 1).limit(30)
    return list(cursor)

@app.get("/api/movies/{movie_id}/insights", response_model=List[Insight])
def get_insights(movie_id: str):
    if db is None: raise HTTPException(500, "DB Connection Failed")
    
    cursor = db.insights.find({"movie_id": movie_id}).sort("generated_at", -1).limit(20)
    return list(cursor)

@app.get("/api/movies/{movie_id}/feed")
def get_feed(movie_id: str, limit: int = 50):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
