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

    # Intelligent Validation
    from agents.validator import ContentValidator
    validator = ContentValidator()
    
    # Validate based on Plot
    plot = data.get("metadata", {}).get("Plot", "")
    if not validator.validate(plot, movie_title, "imdb_plot"):
        logger.warning(f"   IMDB data for '{movie_title}' passed manual check but failed intelligent validation.")
        # We might choose to return empty, or log and proceed if we trust strict title match more.
        # Given "Soyuz 13" example, we should trust validation.
        return {"signals": []}

    # 1. Update Movie Metadata in DB (IMDB-specific fields only)
    meta = data.get("metadata", {})
    if meta:
        try:
            mongo = MongoDBClient()
            db = mongo.get_db()
            
            # Parse IMDB rating and votes
            imdb_rating = float(meta.get("imdbRating", 0)) if meta.get("imdbRating") != "N/A" else None
            imdb_votes = int(meta.get("imdbVotes", "0").replace(",", "")) if meta.get("imdbVotes") != "N/A" else None
            
            # Parse Ratings array for Rotten Tomatoes (supplementary)
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
            
            # Build update document - ONLY IMDB-specific fields
            update_fields = {
                # Nested IMDB data
                "imdb.rating": imdb_rating,
                "imdb.votes": imdb_votes,
                
                # Flat fields for backward compatibility
                "imdb_rating": imdb_rating,
                "imdb_votes": imdb_votes,
            }
            
            # Add Rotten Tomatoes data if available (only if not already set by TMDB)
            if rotten_tomatoes_score is not None:
                update_fields["rotten_tomatoes.critics_score"] = rotten_tomatoes_score
            
            # Add Metascore if available (only if not already set by TMDB)
            if meta.get("Metascore") and meta.get("Metascore") != "N/A":
                try:
                    update_fields["metascore"] = int(meta.get("Metascore"))
                except:
                    pass
            
            # Add Box Office if available (OMDB preferred over TMDB revenue)
            if meta.get("BoxOffice") and meta.get("BoxOffice") != "N/A":
                update_fields["box_office"] = meta.get("BoxOffice")
            
            # Add Awards if available (OMDB only)
            if meta.get("Awards") and meta.get("Awards") != "N/A":
                update_fields["awards"] = meta.get("Awards")
            
            # Add Poster if available (OMDB) - CRITICAL FIX
            # Use 'poster_url' to match schema used by TMDB node
            if meta.get("Poster") and meta.get("Poster") != "N/A":
                update_fields["poster_url"] = meta.get("Poster")
            
            # Remove None/Empty values to avoid overwriting with garbage
            update_fields = {k: v for k, v in update_fields.items() if v is not None}
            
            if not update_fields:
                logger.warning("   No IMDB data to update.")
                return {"signals": []}
            
            # Smart query handling
            from bson import ObjectId
            query = {"_id": movie_id}
            if isinstance(movie_id, str):
                if ObjectId.is_valid(movie_id):
                    query = {"_id": ObjectId(movie_id)}
                else:
                    query = {"movie_id": movie_id}

            # Update only if we have data
            db.movies.update_one(
                query,
                {"$set": update_fields},
                upsert=False  # Don't create if doesn't exist
            )
            logger.info(f"   ✅ Updated IMDB-specific fields (Rating: {imdb_rating}, Votes: {imdb_votes})")
            
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
