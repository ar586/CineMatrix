import logging
from agents.state import AgentState, SourceSentiment
from backend.datasources.imdb.client import IMDBClient
from backend.database.client import MongoDBClient

logger = logging.getLogger(__name__)

def imdb_agent_node(state: AgentState):
    """
    LangGraph node for IMDB/OMDB data fetching.
    """
    movie_title = state["movie_title"]
    movie_id = state["movie_id"]
    logger.info(f"⭐ [IMDB Agent] Activated for: {movie_title}")

    client = IMDBClient()
    data = client.fetch_movie_data(movie_title)
    
    if not data or "reviews" not in data:
        logger.warning("   No IMDB data found.")
        return {"signals": []}

    # 1. Update Movie Metadata in DB
    meta = data.get("metadata", {})
    if meta:
        try:
            mongo = MongoDBClient()
            db = mongo.get_db()
            
            # Parse OMDB fields
            genres = [g.strip() for g in meta.get("Genre", "").split(",")] if meta.get("Genre") else []
            runtime_str = meta.get("Runtime", "0 min").split(" ")[0]
            runtime = int(runtime_str) if runtime_str.isdigit() else 0
            
            # Parse Ratings array for Rotten Tomatoes
            rotten_tomatoes_score = None
            metacritic_score = None
            ratings = meta.get("Ratings", [])
            for rating in ratings:
                if rating.get("Source") == "Rotten Tomatoes":
                    # Extract percentage (e.g., "93%" -> 93)
                    rt_value = rating.get("Value", "").replace("%", "")
                    try:
                        rotten_tomatoes_score = int(rt_value)
                    except:
                        pass
                elif rating.get("Source") == "Metacritic":
                    # Extract score (e.g., "68/100" -> 68)
                    mc_value = rating.get("Value", "").split("/")[0]
                    try:
                        metacritic_score = int(mc_value)
                    except:
                        pass
            
            # Parse release date
            release_date = None
            if meta.get("Released") and meta.get("Released") != "N/A":
                try:
                    from datetime import datetime
                    release_date = datetime.strptime(meta.get("Released"), "%d %b %Y")
                except:
                    pass
            
            update_fields = {
                "genres": genres,
                "runtime_minutes": runtime,
                "poster_url": meta.get("Poster"),
                "language": meta.get("Language"),
                "release_date": release_date,
                "crew.director": meta.get("Director"),
                "crew.writers": [w.strip() for w in meta.get("Writer", "").split(",")] if meta.get("Writer") else [],
                "cast": [a.strip() for a in meta.get("Actors", "").split(",")] if meta.get("Actors") else [],
                "imdb.rating": float(meta.get("imdbRating", 0)) if meta.get("imdbRating") != "N/A" else 0,
                "imdb.votes": int(meta.get("imdbVotes", "0").replace(",", "")) if meta.get("imdbVotes") != "N/A" else 0,
            }
            
            # Add Rotten Tomatoes data if available
            if rotten_tomatoes_score is not None:
                update_fields["rotten_tomatoes.critics_score"] = rotten_tomatoes_score
            
            # Add Metascore if available
            if meta.get("Metascore") and meta.get("Metascore") != "N/A":
                try:
                    update_fields["metascore"] = int(meta.get("Metascore"))
                except:
                    pass
            
            # Add Box Office if available
            if meta.get("BoxOffice") and meta.get("BoxOffice") != "N/A":
                update_fields["box_office"] = meta.get("BoxOffice")
            
            # Add Awards if available
            if meta.get("Awards") and meta.get("Awards") != "N/A":
                update_fields["awards"] = meta.get("Awards")
            
            # Remove None/Empty values to avoid overwriting with garbage
            update_fields = {k: v for k, v in update_fields.items() if v}
            
            db.movies.update_one(
                {"_id": movie_id},
                {"$set": update_fields}
            )
            logger.info("   ✅ Updated Movie Metadata from OMDB.")
            
        except Exception as e:
            logger.error(f"   Failed to update movie metadata: {e}")
    
    signals = []
    # In the client implementation, 'reviews' currently contains the Plot 
    # but theoretically could contain actual reviews.
    for item in data.get("reviews", []):
        signal: SourceSentiment = {
            "source": "imdb",
            "text": item.get("text", ""),
            "url": f"https://www.imdb.com/title/{data['metadata'].get('imdbID', '')}/",
            "metadata": {
                "rating": item.get("rating"),
                "imdb_id": data["metadata"].get("imdbID")
            }
        }
        signals.append(signal)

    return {"signals": signals}
