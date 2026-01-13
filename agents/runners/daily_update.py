import sys
import os
import time
from datetime import datetime
import logging

# Add project root
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import backend.config # Load Env
from backend.database.client import MongoDBClient
from agents.orchestrator import AgentOrchestrator

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("daily_update.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DailyRunner")

def main():
    logger.info("🚀 Starting Daily Sentiment Update")
    
    # Init DB
    mongo = MongoDBClient()
    db = mongo.get_db()
    if db is None:
        logger.error("❌ Could not connect to database. Aborting.")
        sys.exit(1)
        
    # Init Orchestrator
    orchestrator = AgentOrchestrator()
    
    # Fetch Active Movies
    # Note: If 'is_active' is missing (old docs), treat as False or update query
    # We query for { is_active: true }
    cursor = db.movies.find({"is_active": True})
    movies = list(cursor)
    
    logger.info(f"📅 Found {len(movies)} active movies to process.")
    
    for movie in movies:
        movie_title = movie.get("title")
        movie_id = movie.get("movie_id")
        
        if not movie_id or not movie_title:
            logger.warning(f"⚠️ Skipping invalid movie record: {movie.get('_id')}")
            continue
            
        try:
            logger.info(f"👉 Processing: {movie_title}...")
            orchestrator.process_movie(movie_id, movie_title)
            # Sleep briefly to avoid rate limits
            time.sleep(2) 
        except Exception as e:
            logger.error(f"❌ Failed to process {movie_title}: {e}")
            
    logger.info("🏁 Daily Update Completed.")

if __name__ == "__main__":
    main()
