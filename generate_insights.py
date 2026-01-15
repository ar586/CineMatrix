"""
Generate sample insights for movies that have sentiment data but no insights.
This is a temporary script to populate insights for testing.
"""
import sys
import os
sys.path.append(os.getcwd())

from backend import config
from backend.database.client import MongoDBClient
from backend.database.models import Insight, Evidence, RecommendedVisual, GeneratorInfo
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenerateInsights")

def generate_sample_insights(movie_id: str, movie_title: str):
    """Generate sample insights for a movie"""
    
    client = MongoDBClient()
    db = client.get_db()
    
    # Check if insights already exist
    existing = db.insights.count_documents({"movie_id": movie_id})
    if existing > 0:
        logger.info(f"Movie {movie_title} already has {existing} insights")
        return
    
    # Get sentiment data to base insights on
    sentiments = list(db.daily_sentiments.find({"movie_id": movie_id}).sort("date", -1).limit(7))
    
    if not sentiments:
        logger.warning(f"No sentiment data found for {movie_title}")
        return
    
    # Calculate average sentiment
    avg_sentiment = sum(s.get("overall_sentiment", 0) for s in sentiments) / len(sentiments)
    
    # Generate insights based on sentiment
    insights_to_create = []
    
    # Insight 1: Overall Reception
    if avg_sentiment > 0.7:
        insights_to_create.append({
            "title": "Strong Positive Reception",
            "summary": f"{movie_title} is receiving overwhelmingly positive feedback across social media platforms, with an average sentiment score of {avg_sentiment:.2f}.",
            "insight_type": "trend",
            "severity": "low"
        })
    elif avg_sentiment < 0.3:
        insights_to_create.append({
            "title": "Mixed Critical Response",
            "summary": f"{movie_title} shows polarized audience reactions with an average sentiment of {avg_sentiment:.2f}, indicating divided opinions.",
            "insight_type": "polarization",
            "severity": "medium"
        })
    else:
        insights_to_create.append({
            "title": "Moderate Audience Engagement",
            "summary": f"{movie_title} maintains steady audience interest with balanced sentiment scores around {avg_sentiment:.2f}.",
            "insight_type": "trend",
            "severity": "low"
        })
    
    # Insight 2: Volume-based
    total_volume = 0
    for s in sentiments:
        vol = s.get("volume", 0)
        if isinstance(vol, dict):
            total_volume += vol.get("reddit_posts", 0) + vol.get("youtube_videos", 0)
        elif isinstance(vol, int):
            total_volume += vol
    
    
    if total_volume > 50:
        insights_to_create.append({
            "title": "High Social Media Activity",
            "summary": f"Significant online discussion detected with {total_volume} total mentions across platforms in the past week.",
            "insight_type": "trend",
            "severity": "low"
        })
    
    # Insight 3: Aspect-based (if available)
    if sentiments and sentiments[0].get("aspect_summary"):
        aspects = sentiments[0]["aspect_summary"]
        top_aspect = max(aspects.items(), key=lambda x: x[1]) if aspects else None
        
        if top_aspect:
            insights_to_create.append({
                "title": f"Strong {top_aspect[0].title()} Praise",
                "summary": f"Audiences particularly appreciate the {top_aspect[0]} aspect, with a score of {top_aspect[1]:.2f}.",
                "insight_type": "reception_shift",
                "severity": "low"
            })
    
    # Store insights
    for insight_data in insights_to_create:
        insight = Insight(
            movie_id=movie_id,
            insight_type=insight_data["insight_type"],
            severity=insight_data["severity"],
            title=insight_data["title"],
            summary=insight_data["summary"],
            evidence=Evidence(
                related_events=[],
                sentiment_change=None,
                interest_change=None
            ),
            recommended_visual=RecommendedVisual(
                component="line_chart",
                x="date",
                y=["sentiment"]
            ),
            confidence=0.75,
            generated_by=GeneratorInfo(
                agent="sample_insight_generator",
                version="1.0"
            ),
            generated_at=datetime.now(timezone.utc)
        )
        
        try:
            insight_dict = insight.model_dump(by_alias=True, exclude_none=True)
            db.insights.insert_one(insight_dict)
            logger.info(f"✅ Created insight: {insight_data['title']}")
        except Exception as e:
            logger.error(f"❌ Failed to create insight: {e}")

if __name__ == "__main__":
    # Generate insights for movies with sentiment data
    client = MongoDBClient()
    db = client.get_db()
    
    movies = [
        ("tt1457767", "The Conjuring"),
        ("tt1591095", "Insidious"),
        ("tt1375666", "Inception")
    ]
    
    for movie_id, movie_title in movies:
        logger.info(f"Generating insights for {movie_title}...")
        generate_sample_insights(movie_id, movie_title)
    
    logger.info("✅ Insight generation complete!")
