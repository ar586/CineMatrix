import sys
import os
import logging
from datetime import datetime, timedelta

# Path setup to ensure backend modules match
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ReleaseFetcher")

try:
    from backend.datasources.tmdb.client import TMDBClient
    from backend.database.client import MongoDBClient
    from agents.orchestrator import AgentOrchestrator
except ImportError as e:
    logger.error(f"Import Error: {e}")
    sys.exit(1)

def fetch_and_ingest():
    logger.info("🎬 Starting Weekly Release Automation...")
    tmdb = TMDBClient()
    mongo = MongoDBClient()
    db = mongo.get_db()
    orch = AgentOrchestrator()
    
    # ---------------------------------------------------------
    # 1. Discover New Movies (Hindi, India, Last 4 weeks)
    # Using 28 days window to ensure we catch recent releases
    # ---------------------------------------------------------
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    logger.info(f"🔍 Checking for new Hindi releases in India since {start_date}...")
    try:
        new_releases = tmdb.discover_movies(
            region="IN", 
            language="hi", 
            release_date_gte=start_date
        )
    except Exception as e:
        logger.error(f"TMDB Discovery failed: {e}")
        new_releases = []
    
    logger.info(f"   Found {len(new_releases)} candidates from TMDB.")
    
    ingested_count = 0
    for m in new_releases:
        title = m.get("title")
        tmdb_id = m.get("id")
        
        # Determine IMDB ID (Critical for our system)
        details = tmdb.get_movie_details(tmdb_id)
        if not details: 
            continue
            
        imdb_id = details.get("imdb_id")
        if not imdb_id:
            logger.info(f"   ⚠️ Skipping '{title}' (No IMDB ID).")
            continue
            
        # Check Existence in Database
        exists = db.movies.find_one({"movie_id": imdb_id})
        if exists:
            # logger.info(f"   Skipping '{title}' (Already Ingested).")
            continue
            
        logger.info(f"🚀 Ingesting NEW Movie: {title} ({imdb_id})")
        try:
            # Trigger Pipeline
            orch.process_movie(imdb_id, title)
            
            # Set Active Explicitly
            db.movies.update_one(
                {"movie_id": imdb_id},
                {"$set": {"is_active": True}}
            )
            ingested_count += 1
            logger.info(f"   ✅ Successfully ingested '{title}'.")
            
        except Exception as e:
            logger.error(f"   ❌ Ingestion failed for {title}: {e}")

    logger.info(f"📊 Ingestion complete. Added {ingested_count} new movies.")
    
    # ---------------------------------------------------------
    # 2. Lifecycle Cleanup (Archive Old Movies)
    # ---------------------------------------------------------
    logger.info("🧹 Performing Lifecycle Cleanup...")
    # Movies older than 2 weeks (14 days) set to inactive
    cutoff_date = datetime.now() - timedelta(days=14)
    
    # Find active movies
    active_movies = db.movies.find({"is_active": True})
    archived_count = 0
    
    for movie in active_movies:
        # Check release date
        r_date = movie.get("release_date")
        
        # Parse date if strictly necessary (Pydantic usually handles it, but raw MongoDB query returns stored type)
        # If stored as string (ISO), parse it. If datetime, compare directly.
        if r_date:
            parsed_date = None
            if isinstance(r_date, datetime):
                parsed_date = r_date
            elif isinstance(r_date, str):
                try:
                    parsed_date = datetime.fromisoformat(r_date.replace("Z", "+00:00"))
                except:
                    pass
            
            if parsed_date and parsed_date < cutoff_date:
                db.movies.update_one(
                    {"_id": movie["_id"]},
                    {"$set": {"is_active": False}}
                )
                logger.info(f"   📦 Archived '{movie.get('title')}' (Released: {parsed_date.date()})")
                archived_count += 1
                
    logger.info(f"✅ Lifecycle Cleanup Complete. Archived {archived_count} movies.")

if __name__ == "__main__":
    fetch_and_ingest()
