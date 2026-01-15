"""
Script to fetch TMDB data (including posters) for movies missing it
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import backend.config
from backend.database.client import MongoDBClient
from agents.nodes.tmdb_node import tmdb_agent_node
from agents.state import AgentState

def fetch_missing_posters():
    """Fetch TMDB data for movies that don't have it"""
    
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    if db is None:
        print("❌ Could not connect to database")
        return
    
    # Find movies without TMDB data
    movies = list(db.movies.find({
        "$or": [
            {"tmdb_id": None},
            {"tmdb_id": {"$exists": False}},
            {"poster_url": None},
            {"poster_url": {"$exists": False}}
        ]
    }, {"_id": 1, "title": 1}))
    
    print(f"Found {len(movies)} movies without TMDB data\n")
    
    for movie in movies:
        movie_id = movie["_id"]
        movie_title = movie["title"]
        
        print(f"🎬 Fetching TMDB data for: {movie_title}")
        
        try:
            state = AgentState(
                movie_id=movie_id,
                movie_title=movie_title,
                signals=[],
                errors=[],
                cast=[],
                news_articles=[]
            )
            
            tmdb_agent_node(state)
            
            # Check if poster was added
            updated_movie = db.movies.find_one({"_id": movie_id}, {"poster_url": 1, "tmdb_id": 1})
            if updated_movie.get("poster_url"):
                print(f"   ✅ Poster added: {updated_movie['poster_url'][:60]}...")
            elif updated_movie.get("tmdb_id"):
                print(f"   ⚠️  TMDB ID found but no poster available")
            else:
                print(f"   ❌ No TMDB data found for this movie")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    fetch_missing_posters()
