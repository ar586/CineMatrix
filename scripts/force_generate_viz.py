"""
Force generate daily sentiments and visualizations for all movies with raw data.
This bypasses the normal pipeline to fix missing numerical data.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient
from backend.aggregation.aggregator import SentimentAggregator
from agents.nodes.visualization_node import VisualizationGenerator
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForceViz")

def main():
    client = MongoDBClient()
    db = client.get_db()
    
    if db is None:
        logger.error("Failed to connect to database")
        return
    
    # Get all movies
    movies = list(db.movies.find({}))
    logger.info(f"Found {len(movies)} movies")
    
    aggregator = SentimentAggregator()
    viz_gen = VisualizationGenerator()
    
    for movie in movies:
        movie_id = movie.get("movie_id", str(movie["_id"]))
        title = movie.get("title", "Unknown")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {title} ({movie_id})")
        
        # Check if we have source sentiments
        sentiment_count = db.source_sentiments.count_documents({"movie_id": movie_id})
        logger.info(f"  Source sentiments: {sentiment_count}")
        
        if sentiment_count == 0:
            logger.warning(f"  ⚠️  No source sentiments - skipping")
            continue
        
        # Force aggregation
        try:
            logger.info("  Running aggregation...")
            daily_sentiment = aggregator.aggregate_daily_sentiment(movie_id, datetime.now(timezone.utc))
            
            if daily_sentiment:
                logger.info(f"  ✅ Created daily sentiment record")
            else:
                logger.warning(f"  ⚠️  Aggregation returned None")
        except Exception as e:
            logger.error(f"  ❌ Aggregation failed: {e}")
            continue
        
        # Force visualization generation
        try:
            logger.info("  Generating visualizations...")
            viz_gen.generate_and_cache(movie_id, title)
            logger.info(f"  ✅ Visualizations generated")
        except Exception as e:
            logger.error(f"  ❌ Visualization generation failed: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info("Processing complete!")
    
    # Summary
    total_daily = db.daily_movie_sentiments.count_documents({})
    total_viz = db.visualization_components.count_documents({})
    logger.info(f"Total daily sentiments in DB: {total_daily}")
    logger.info(f"Total visualizations in DB: {total_viz}")

if __name__ == "__main__":
    main()
