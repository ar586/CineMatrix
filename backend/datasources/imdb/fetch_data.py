

from .client import IMDBClient
from .parser import IMDBParser
from ..tmdb.client import TMDBClient
from ..tmdb.parser import TMDBParser as TMDBDataParser
import os
import logging

logger = logging.getLogger(__name__)

class MovieDataFetcher:
    def __init__(self):
        self.imdb_client = IMDBClient()
        self.imdb_parser = IMDBParser()
        self.tmdb_client = TMDBClient()
        self.tmdb_parser = TMDBDataParser()

    def get_movie_details(self, title):
        """
        Fetch movie details using TMDB as primary, OMDB as secondary/fallback.
        """
        movie_data = {}
        
        # 1. Fetch from TMDB (Primary)
        try:
            print(f"Fetching TMDB data for: {title}")
            tmdb_raw = self.tmdb_client.get_full_movie_data(title)
            if tmdb_raw:
                movie_data = self.tmdb_parser.parse_movie(tmdb_raw)
        except Exception as e:
            logger.error(f"TMDB Fetch Error: {e}")
            print(f"TMDB Fetch Error: {e}")

        # 2. Fetch from OMDB (Secondary - for Ratings & ID Fallback)
        try:
            print(f"Fetching OMDB data for: {title}")
            omdb_raw = self.imdb_client.search_movie(title)
            omdb_data = self.imdb_parser.parse_movie(omdb_raw)
            
            if omdb_data:
                # If TMDB failed completely, use OMDB data
                if not movie_data:
                    movie_data = omdb_data
                    # Map OMDB specific fields to schema
                    movie_data["movie_id"] = omdb_data.get("imdb_id")
                    movie_data["runtime_minutes"] = int(omdb_data["runtime"].split(" ")[0]) if omdb_data.get("runtime") and "min" in omdb_data["runtime"] else None
                    
                    # Normalize Ratings structure if using OMDB as primary
                    if omdb_data.get("rotten_tomatoes"):
                         movie_data["rotten_tomatoes"] = {"critics_score": omdb_data["rotten_tomatoes"]}
                         
                    if omdb_data.get("metascore"):
                        movie_data["metascore"] = omdb_data["metascore"] # Already int, schema expects int or dict?
                        # Model says: metascore: Optional[int] = None. So int is fine.
                        
                else:
                    # Merge OMDB data into TMDB data
                    # Ratings
                    if omdb_data.get("rotten_tomatoes"):
                        movie_data["rotten_tomatoes"] = {"critics_score": omdb_data["rotten_tomatoes"]}
                    
                    if omdb_data.get("metascore"):
                        movie_data["metascore"] = omdb_data["metascore"]
                        
                    if omdb_data.get("imdb_rating"):
                        if not movie_data.get("imdb"): movie_data["imdb"] = {}
                        movie_data["imdb"]["rating"] = omdb_data["imdb_rating"]
                        movie_data["imdb"]["votes"] = omdb_data["imdb_votes"]
                        
                    if omdb_data.get("box_office") and not movie_data.get("box_office"):
                        movie_data["box_office"] = omdb_data["box_office"]
                        
                    if omdb_data.get("awards"):
                        movie_data["awards"] = omdb_data["awards"]
                        
        except Exception as e:
            logger.error(f"OMDB Fetch Error: {e}")
            print(f"OMDB Fetch Error: {e}")
            
        return movie_data


