
import sys
import os
import logging
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import backend.config
from backend.database.client import MongoDBClient
from backend.datasources.imdb.fetch_data import MovieDataFetcher
from backend.datasources.wikipedia.fetch_pages import MovieFetcher as WikiFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def refresh_metadata():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    # Get all active movies
    movies = list(db.movies.find({"is_active": True}))
    logger.info(f"Found {len(movies)} active movies to refresh.")
    
    data_fetcher = MovieDataFetcher()
    wiki_fetcher = WikiFetcher()
    
    for movie in movies:
        title = movie["title"]
        movie_id = movie["_id"]
        logger.info(f"Refreshing metadata for: {title}")
        
        updates = {}
        
        # 1. Fetch TMDB/OMDB Data
        try:
            metadata = data_fetcher.get_movie_details(title)
            if metadata:
                # Merge into updates. Note: We need to be careful not to overwrite some fields if we want to keep them.
                # However, since we want the latest rich data, we will overwrite most.
                # We convert pydantic/dict to update dict
                updates.update(metadata)
        except Exception as e:
            logger.error(f"Failed to fetch metadata for {title}: {e}")
            
        # 2. Fetch Wikipedia Data
        try:
            wiki_data = wiki_fetcher.get_movie_info(title)
            if wiki_data:
                updates["wikipedia"] = wiki_data
        except Exception as e:
            logger.error(f"Failed to fetch Wikipedia for {title}: {e}")
            
        if updates:
            updates["updated_at"] = datetime.utcnow()
            
            # Remove fields that shouldn't be overridden if they exist and are important?
            # actually, our parser output should be the source of truth.
            
            # Update DB
            db.movies.update_one(
                {"_id": movie_id},
                {"$set": updates}
            )
            logger.info(f"✅ Updated {title}")
        else:
            logger.warning(f"No updates found for {title}")

if __name__ == "__main__":
    refresh_metadata()
