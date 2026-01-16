from datetime import datetime
from typing import Dict, Any, Optional

class TMDBParser:
    def parse_movie(self, tmdb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse TMDB full data into our internal Movie structure.
        """
        details = tmdb_data.get("details", {})
        images = tmdb_data.get("images", {})
        videos = tmdb_data.get("videos", [])
        credits = tmdb_data.get("credits", {})
        
        if not details:
            return None
            
        # Parse Release Date
        release_date = None
        if details.get("release_date"):
            try:
                release_date = datetime.strptime(details["release_date"], "%Y-%m-%d")
            except ValueError:
                pass
                
        # Parse Crew (Director, Writers)
        crew_data = credits.get("crew", [])
        directors = [m["name"] for m in crew_data if m["job"] == "Director"]
        writers = [m["name"] for m in crew_data if m["department"] == "Writing"]
        
        # Parse Cast (Top 10)
        cast_data = credits.get("cast", [])
        cast = [m["name"] for m in cast_data[:10]]
        
        # Parse Production Companies
        production_companies = [c["name"] for c in details.get("production_companies", [])]
        
        return {
            "movie_id": details.get("imdb_id"), # Prefer IMDB ID for consistency if available
            "tmdb_id": details.get("id"),
            "title": details.get("title"),
            "original_title": details.get("original_title"),
            "language": details.get("original_language"),
            "release_date": release_date,
            "runtime_minutes": details.get("runtime"),
            "genres": [g["name"] for g in details.get("genres", [])],
            "overview": details.get("overview"),
            "tagline": details.get("tagline"),
            "poster_url": images.get("poster") or images.get("poster_high_res"),
            "backdrop_url": images.get("backdrop"),
            "budget": details.get("budget"),
            "revenue": details.get("revenue"),
            "popularity": details.get("popularity"),
            "vote_average": details.get("vote_average"),
            "vote_count": details.get("vote_count"),
            "crew": {
                "director": directors[0] if directors else None,
                "writers": list(set(writers)), # Unique writers
                "producers": [] # Can add if needed
            },
            "cast": cast,
            "production_companies": production_companies,
            "trailers": videos,
            "collection": details.get("belongs_to_collection"),
            "updated_at": datetime.utcnow()
        }
