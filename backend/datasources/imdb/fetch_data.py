
from .client import IMDBClient
from .parser import IMDBParser
import os

class IMDBFetcher:
    def __init__(self):
        self.client = IMDBClient()
        self.parser = IMDBParser()

    def get_movie_details(self, title):
        """
        Fetch movie details from IMDB (via OMDB).
        """
        try:
            # Check for API key before attempting request to save a call
            if not self.client.api_key:
                print("IMDB_API_KEY is missing. Skipping IMDB fetch.")
                return None

            data = self.client.search_movie(title)
            return self.parser.parse_movie(data)
            
        except Exception as e:
            print(f"Error fetching IMDB data for {title}: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    # Ensure IMDB_API_KEY is set in env
    fetcher = IMDBFetcher()
    title = "Inception"
    print(f"Fetching IMDB details for {title}...")
    details = fetcher.get_movie_details(title)
    
    if details:
        print(f"Title: {details['title']} ({details['year']})")
        print(f"Rating: {details['imdb_rating']}/10 ({details['imdb_votes']} votes)")
        print(f"Plot: {details['plot']}")
    else:
        print("Movie not found or error occurred.")
