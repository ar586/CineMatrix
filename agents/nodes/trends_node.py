import logging
from agents.state import AgentState
from backend.datasources.google_trends.fetch_trends import TrendsFetcher
from backend.database.client import MongoDBClient
from datetime import datetime

logger = logging.getLogger(__name__)

def trends_agent_node(state: AgentState):
    """
    LangGraph node for Google Trends data fetching.
    """
    movie_title = state["movie_title"]
    movie_id = state.get("movie_id")
    
    logger.info(f"📈 [Trends Agent] Activated for: {movie_title}")
    
    try:
        fetcher = TrendsFetcher()
        data = fetcher.get_movie_trends(movie_title)
        
        if not data:
            logger.warning("   No Trends data found.")
            return {}
            
        # Intelligent Validation
        # Trends data is numeric, harder to validate textually.
        # But we can check 'related_queries' if they mention 'movie', 'film', 'cast' or the title variants.
        from agents.validator import ContentValidator
        validator = ContentValidator()
        
        related_queries_dict = data.get("related_queries", {})
        related_top = []
        
        # Try exact match first
        if movie_title in related_queries_dict:
             related_top = related_queries_dict[movie_title].get("top", [])
        # Fallback: take the first key if available (SerpApi might normalize query)
        elif related_queries_dict:
             first_key = next(iter(related_queries_dict))
             related_top = related_queries_dict[first_key].get("top", [])
             
        if related_top:
            # Construct a context string from related queries
            related_str = ", ".join([q["query"] for q in related_top[:5]])
            if not validator.validate(f"Related Queries: {related_str}", movie_title, "google_trends_context"):
                logger.warning(f"   Trends data validation failed. Related queries: {related_str}")
                return {} # Reject if trends seem completely unrelated (e.g. generic term)

        # Save to DB
        mongo = MongoDBClient()
        db = mongo.get_db()
        data["movie_id"] = movie_id
        data["ingested_at"] = datetime.utcnow()
        
        db.google_trends.update_one(
            {"movie_id": movie_id, "timeframe": data.get("timeframe")},
            {"$set": data},
            upsert=True
        )
        logger.info("   ✅ Saved Trends data to DB.")
        
        return {} # No signals to pass, just side-effect save
        
    except Exception as e:
        logger.error(f"   ❌ Trends fetch failed: {e}")
        return {"errors": [str(e)]}
