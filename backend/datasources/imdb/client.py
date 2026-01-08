
import requests
import os

class IMDBClient:
    BASE_URL = "http://www.omdbapi.com/"

    def __init__(self):
        """
        Initialize IMDB/OMDB Client.
        Expects 'IMDB_API_KEY' in environment variables.
        """
        self.api_key = os.getenv("IMDB_API_KEY")

    def search_movie(self, title):
        """
        Search for a movie by title.
        Returns the raw JSON response from OMDB.
        """
        if not self.api_key:
            raise ValueError("IMDB_API_KEY not found in environment variables.")

        params = {
            "apikey": self.api_key,
            "t": title,
            "type": "movie"  # Limit to movies
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"OMDB API Request Error: {e}")
            return None
