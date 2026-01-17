import os
import requests
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class TMDBClient:
    """Client for The Movie Database (TMDB) API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"
    
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.access_token = os.getenv("TMDB_ACCESS_TOKEN")
        
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment variables")
        
        # Use Bearer token for authentication (recommended by TMDB)
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        } if self.access_token else {}
    
    def search_movie(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Search for a movie by title.
        Returns the first result with TMDB ID and basic info.
        """
        results = self.search_movies(title, year)
        return results[0] if results else None

    def search_movies(self, title: str, year: Optional[int] = None) -> List[Dict]:
        """
        Search for movies by title.
        Returns list of results.
        """
        params = {
            "api_key": self.api_key,
            "query": title,
            "include_adult": False
        }
        
        if year:
            params["year"] = year
        
        try:
            # Create session with retry strategy
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount("https://", adapter)
            
            response = session.get(
                f"{self.BASE_URL}/search/movie",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("results", [])
        except Exception as e:
            logger.error(f"TMDB search failed for '{title}': {e}")
            return []
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get detailed movie information by TMDB ID.
        Includes: budget, revenue, runtime, genres, production companies, etc.
        """
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/movie/{tmdb_id}",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get TMDB details for ID {tmdb_id}: {e}")
            return None
    
    def get_movie_images(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get movie images (posters, backdrops).
        Returns URLs for different sizes.
        """
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/movie/{tmdb_id}/images",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Get best poster and backdrop
            result = {}
            if data.get("posters"):
                poster = data["posters"][0]  # Highest rated
                result["poster"] = f"{self.IMAGE_BASE_URL}/w500{poster['file_path']}"
                result["poster_high_res"] = f"{self.IMAGE_BASE_URL}/original{poster['file_path']}"
            
            if data.get("backdrops"):
                backdrop = data["backdrops"][0]
                result["backdrop"] = f"{self.IMAGE_BASE_URL}/w1280{backdrop['file_path']}"
            
            return result
        except Exception as e:
            logger.error(f"Failed to get images for TMDB ID {tmdb_id}: {e}")
            return None
    
    def get_movie_videos(self, tmdb_id: int) -> List[Dict]:
        """
        Get movie videos (trailers, teasers, clips).
        Returns list of YouTube video keys.
        """
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/movie/{tmdb_id}/videos",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter for trailers and teasers
            videos = []
            for video in data.get("results", []):
                if video.get("site") == "YouTube" and video.get("type") in ["Trailer", "Teaser"]:
                    videos.append({
                        "key": video["key"],
                        "name": video["name"],
                        "type": video["type"],
                        "url": f"https://www.youtube.com/watch?v={video['key']}"
                    })
            
            return videos
        except Exception as e:
            logger.error(f"Failed to get videos for TMDB ID {tmdb_id}: {e}")
            return []
    
    def get_movie_credits(self, tmdb_id: int) -> Optional[Dict]:
        """
        Get movie cast and crew.
        Returns detailed cast/crew information.
        """
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/movie/{tmdb_id}/credits",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get credits for TMDB ID {tmdb_id}: {e}")
            return None
    
    def get_now_playing(self, page: int = 1) -> List[Dict]:
        """
        Get movies currently in theaters.
        Great for discovering trending movies.
        """
        params = {
            "api_key": self.api_key,
            "page": page,
            "region": "US"  # Can be customized
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/movie/now_playing",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Failed to get now playing movies: {e}")
            return []
    
    
    def discover_movies(self, region: str = "US", language: str = "en", release_date_gte: str = None) -> List[Dict]:
        """
        Discover movies with advanced filters.
        """
        params = {
            "api_key": self.api_key,
            "sort_by": "popularity.desc",
            "include_adult": False,
            "include_video": False,
            "page": 1,
            "region": region,
            "with_original_language": language
        }
        
        if release_date_gte:
            params["primary_release_date.gte"] = release_date_gte

        try:
            response = requests.get(
                f"{self.BASE_URL}/discover/movie",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Failed to discover movies: {e}")
            return []
    
    def get_full_movie_data(self, title: str, year: Optional[int] = None) -> Optional[Dict]:
        """
        Convenience method to get all movie data in one call.
        Searches by title, then fetches details, images, videos, and credits.
        """
        # Search for movie
        search_result = self.search_movie(title, year)
        if not search_result:
            return None
        
        tmdb_id = search_result["id"]
        
        # Fetch all data
        details = self.get_movie_details(tmdb_id)
        images = self.get_movie_images(tmdb_id)
        videos = self.get_movie_videos(tmdb_id)
        credits = self.get_movie_credits(tmdb_id)
        
        return {
            "tmdb_id": tmdb_id,
            "details": details,
            "images": images,
            "videos": videos,
            "credits": credits
        }
