import logging
from agents.state import AgentState
from backend.datasources.tmdb.client import TMDBClient
from backend.database.client import MongoDBClient
from datetime import datetime

logger = logging.getLogger(__name__)

def tmdb_agent_node(state: AgentState):
    """
    LangGraph node for TMDB data fetching.
    Fetches enhanced metadata: posters, budgets, trailers, production companies.
    """
    movie_title = state["movie_title"]
    movie_id = state["movie_id"]
    
    logger.info(f"🎬 [TMDB Agent] Activated for: {movie_title}")
    
    try:
        client = TMDBClient()
        
        # Get full movie data from TMDB
        tmdb_data = client.get_full_movie_data(movie_title)
        
        if not tmdb_data:
            logger.warning("   No TMDB data found.")
            return {}
        
        details = tmdb_data.get("details") or {}
        images = tmdb_data.get("images") or {}
        videos = tmdb_data.get("videos") or []
        credits = tmdb_data.get("credits") or {}
        
        # Update Movie document in MongoDB
        mongo = MongoDBClient()
        db = mongo.get_db()
        
        # Parse release date
        release_date = None
        if details.get("release_date"):
            try:
                release_date = datetime.strptime(details["release_date"], "%Y-%m-%d")
            except:
                pass
        
        # Extract cast (top 10)
        cast_list = []
        if credits.get("cast"):
            cast_list = [actor["name"] for actor in credits["cast"][:10]]
        
        # Extract crew (director, writers)
        director = None
        writers = []
        if credits.get("crew"):
            for person in credits["crew"]:
                if person["job"] == "Director" and not director:
                    director = person["name"]
                elif person["department"] == "Writing":
                    writers.append(person["name"])
        
        # Extract production companies
        production_companies = []
        if details.get("production_companies"):
            production_companies = [company["name"] for company in details["production_companies"][:3]]
        
        # Build update document
        update_fields = {
            "tmdb_id": tmdb_data["tmdb_id"],
            "budget": details.get("budget", 0),
            "revenue": details.get("revenue", 0),
            "runtime_minutes": details.get("runtime"),
            "release_date": release_date,
            "genres": [g["name"] for g in details.get("genres", [])],
            "production_companies": production_companies,
            "tagline": details.get("tagline"),
            "overview": details.get("overview"),  # Plot summary
            "popularity": details.get("popularity"),
            "vote_average": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
        }
        
        # Add images
        if images:
            update_fields["poster_url"] = images.get("poster")
            update_fields["backdrop_url"] = images.get("backdrop")
        
        # Add trailers
        if videos:
            update_fields["trailers"] = videos[:3]  # Top 3 trailers
        
        # Add cast/crew
        if cast_list:
            update_fields["cast"] = cast_list
        if director:
            update_fields["crew.director"] = director
        if writers:
            update_fields["crew.writers"] = writers[:5]
        
        # Add collection info if part of franchise
        if details.get("belongs_to_collection"):
            collection = details["belongs_to_collection"]
            update_fields["collection"] = {
                "id": collection["id"],
                "name": collection["name"],
                "poster": collection.get("poster_path")
            }
        
        # Remove None/empty values
        update_fields = {k: v for k, v in update_fields.items() if v not in [None, "", 0, []]}
        
        # Add title to ensure it exists on upsert
        update_fields["title"] = details.get("title", movie_title)
        
        # Smart query handling
        from bson import ObjectId
        query = {"_id": movie_id}
        if isinstance(movie_id, str):
            if ObjectId.is_valid(movie_id):
                query = {"_id": ObjectId(movie_id)}
            else:
                query = {"movie_id": movie_id}

        # Update database
        db.movies.update_one(
            query,
            {"$set": update_fields},
            upsert=True
        )
        
        logger.info(f"   ✅ Updated Movie with TMDB data (ID: {tmdb_data['tmdb_id']})")
        logger.info(f"   Budget: ${update_fields.get('budget', 0):,}, Revenue: ${update_fields.get('revenue', 0):,}")
        
        return {}
        
    except Exception as e:
        logger.error(f"   ❌ TMDB fetch failed: {e}")
        return {"errors": [str(e)]}
