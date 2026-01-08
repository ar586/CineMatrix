
from .client import YouTubeClient
from .parser import YouTubeParser
import os

class YouTubeFetcher:
    def __init__(self):
        self.client = YouTubeClient()
        self.parser = YouTubeParser()

    def get_movie_trailers(self, title, max_results=3):
        """
        Fetch official trailers for a movie.
        """
        query = f"{title} official trailer"
        return self._fetch_videos(query, max_results)

    def get_movie_reviews(self, title, max_results=5):
        """
        Fetch movie reviews.
        """
        query = f"{title} movie review"
        return self._fetch_videos(query, max_results)

    def _fetch_videos(self, query, max_results):
        try:
            if not self.client.api_key:
                print("YOUTUBE_API_KEY is missing. Skipping YouTube fetch.")
                return []

            # 1. Search to get IDs
            search_response = self.client.search_videos(query, max_results)
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            
            if not video_ids:
                return []
                
            # 2. Get details for these IDs (to get views, duration)
            details_response = self.client.get_video_details(video_ids)
            
            # 3. Parse
            return self.parser.parse_videos(details_response.get('items', []))
            
        except Exception as e:
            print(f"Error fetching YouTube videos for query '{query}': {e}")
            return []

if __name__ == "__main__":
    fetcher = YouTubeFetcher()
    title = "Inception"
    print(f"Fetching trailers for {title}...")
    trailers = fetcher.get_movie_trailers(title)
    
    if trailers:
        print(f"Found {len(trailers)} trailers:")
        for t in trailers:
            print(f"- {t['title']} ({t['views']} views) [{t['duration']}]")
    else:
        print("No trailers found or API key missing.")
