"""
Aggregate ALL historical sentiment data and generate visualizations.
This will create daily_sentiments for each date that has source_sentiments.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient
from backend.aggregation.aggregator import SentimentAggregator
from agents.nodes.visualization_node import VisualizationGenerator
from datetime import datetime, timezone
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HistoricalAgg")

def main():
    client = MongoDBClient()
    db = client.get_db()
    
    if db is None:
        logger.error("Failed to connect to database")
        return
    
    # Get all unique (movie_id, date) combinations from source_sentiments
    logger.info("Finding all movie-date combinations...")
    pipeline = [
        {
            "$group": {
                "_id": {
                    "movie_id": "$movie_id",
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$processed_at"}}
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.movie_id": 1, "_id.date": 1}}
    ]
    
    combinations = list(db.source_sentiments.aggregate(pipeline))
    logger.info(f"Found {len(combinations)} movie-date combinations to aggregate")
    
    aggregator = SentimentAggregator()
    viz_gen = VisualizationGenerator()
    
    # Group by movie_id
    movies_to_process = defaultdict(list)
    for combo in combinations:
        movie_id = combo["_id"]["movie_id"]
        date_str = combo["_id"]["date"]
        count = combo["count"]
        movies_to_process[movie_id].append((date_str, count))
    
    logger.info(f"Processing {len(movies_to_process)} unique movies\n")
    
    for movie_id, dates in movies_to_process.items():
        # Get movie title
        movie = db.movies.find_one({"movie_id": movie_id})
        title = movie.get("title", "Unknown") if movie else movie_id
        
        logger.info(f"{'='*60}")
        logger.info(f"Movie: {title} ({movie_id})")
        logger.info(f"  Dates with data: {len(dates)}")
        
        # Aggregate each date
        success_count = 0
        for date_str, count in dates:
            try:
                # Parse date string to datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_obj = date_obj.replace(tzinfo=timezone.utc)
                
                logger.info(f"    Aggregating {date_str} ({count} sentiments)...")
                daily_sentiment = aggregator.aggregate_daily_sentiment(movie_id, date_obj)
                
                if daily_sentiment:
                    success_count += 1
                else:
                    logger.warning(f"      ⚠️  Returned None")
            except Exception as e:
                logger.error(f"      ❌ Failed: {e}")
        
        logger.info(f"  ✅ Successfully aggregated {success_count}/{len(dates)} dates")
        
        # Generate visualizations for this movie
        if success_count > 0:
            try:
                logger.info(f"  Generating visualizations...")
                viz_gen.generate_and_cache(movie_id, title)
                logger.info(f"  ✅ Visualizations generated\n")
            except Exception as e:
                logger.error(f"  ❌ Visualization failed: {e}\n")
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("FINAL SUMMARY")
    logger.info(f"{'='*60}")
    
    total_daily = db.daily_movie_sentiments.count_documents({})
    total_viz = db.visualization_components.count_documents({})
    
    logger.info(f"Total daily_sentiments: {total_daily}")
    logger.info(f"Total visualization_components: {total_viz}")
    
    # Show breakdown by movie
    logger.info("\nPer-movie breakdown:")
    for movie_id in movies_to_process.keys():
        movie = db.movies.find_one({"movie_id": movie_id})
        title = movie.get("title", "Unknown") if movie else movie_id
        
        daily_count = db.daily_movie_sentiments.count_documents({"movie_id": movie_id})
        viz_count = db.visualization_components.count_documents({"movie_id": movie_id})
        
        logger.info(f"  {title}: {daily_count} daily records, {viz_count} visualizations")

if __name__ == "__main__":
    main()
