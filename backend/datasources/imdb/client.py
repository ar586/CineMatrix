
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
    
    def fetch_wikipedia_data(self, title):
        """
        Fetch Wikipedia summary for a movie.
        Uses Wikipedia API to get the summary.
        """
        try:
            # Wikipedia API endpoint
            wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            headers = {
                "User-Agent": "CineMatrix/1.0 (Movie Sentiment Analysis Bot)"
            }
            
            # Try exact title first
            wiki_title = title.replace(" ", "_")
            response = requests.get(f"{wiki_url}{wiki_title}", headers=headers)
            
            # If it's a disambiguation page or not found, try with "(film)" suffix
            if response.status_code != 200 or (response.status_code == 200 and response.json().get("type") == "disambiguation"):
                wiki_title = f"{title.replace(' ', '_')}_(film)"
                response = requests.get(f"{wiki_url}{wiki_title}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Only return if it's a standard page (not disambiguation)
                if data.get("type") == "standard":
                    return {
                        "summary": data.get("extract", ""),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    }
        except Exception as e:
            print(f"Wikipedia API Error: {e}")
        return None
    
    def fetch_movie_data(self, title):
        """
        Fetch detailed movie data including plot.
        Returns structured data with reviews (using plot as review for now).
        """
        movie_data = self.search_movie(title)
        if movie_data and movie_data.get("Response") == "True":
            # OMDB doesn't provide reviews, but we can use plot as content
            plot = movie_data.get("Plot", "")
            if plot and plot != "N/A":
                return {
                    "reviews": [{
                        "id": "omdb_plot",
                        "text": f"Plot: {plot}",
                        "rating": float(movie_data.get("imdbRating", 0)) if movie_data.get("imdbRating") != "N/A" else 0
                    }],
                    "metadata": movie_data
                }
        return None
