
from .client import WikipediaClient
from .parser import WikipediaParser

class MovieFetcher:
    def __init__(self):
        self.client = WikipediaClient()
        self.parser = WikipediaParser()

    def get_movie_info(self, title):
        """
        Fetch and parse movie info. 
        Tries to find the movie page directly or with ' (film)' suffix.
        """
        # 1. Try exact title
        page = self.client.get_page(title)
        
        # 2. If valid but ambiguous or redirect, or not exists, try adding " (film)"
        # Note: wikipedia-api handles redirects automatically usually.
        if not page or not page.exists():
            page = self.client.get_page(f"{title} (film)")
        
        # 3. If still fails, we might return None or do a search (if we had search impl).
        # For now, if page exists, we parse it.
        if page and page.exists():
            return self.parser.extract_movie_details(page)
        
        return None

# Simple main for testing
if __name__ == "__main__":
    fetcher = MovieFetcher()
    info = fetcher.get_movie_info("Inception")
    import json
    print(json.dumps(info, indent=2))
