
from .client import FirecrawlClient

class FirecrawlFetcher:
    def __init__(self):
        self.client = FirecrawlClient()
        # Domains to exclude as per user request
        self.excluded_domains = [
            "reddit.com",
            "twitter.com",
            "x.com",
            "youtube.com",
            "imdb.com",
            "rottentomatoes.com"
        ]

    def search_and_scrape(self, query):
        """
        Search the web for the query, excluding specific domains.
        Returns the top results.
        """
        if not self.client.api_key:
            print("FIRECRAWL_API_KEY is missing. Skipping Firecrawl fetch.")
            return None

        # Construct query with exclusions
        # Using Google-style exclusion operators which Firecrawl/LLM searchers often respect
        full_query = query
        for domain in self.excluded_domains:
            full_query += f" -site:{domain}"

        print(f"Searching via Firecrawl: {full_query}")

        try:
            # Try passing options directly if possible, or use 'params' if that's what the SDK wants
            # Based on recent SDKs, options might be passed as a dictionary argument named 'params' or 'options'
            # Let's try passing 'params' as a keyword argument to our wrapper which passes it to app.search
            
            # Note: If previous attempt failed with 'unexpected keyword argument params', 
            # it implies app.search(query, params=...) failed.
            # Let's try to just pass the query first to be safe, or use 'limit' if generic.
            
            # Retrying with a simplified call for verification
            results = self.client.search(full_query)
            return results
        except Exception as e:
            print(f"Firecrawl Error: {e}")
            return None


