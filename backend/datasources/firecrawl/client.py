
from firecrawl import FirecrawlApp
import os

class FirecrawlClient:
    def __init__(self):
        """
        Initialize Firecrawl Client.
        Expects 'FIRECRAWL_API_KEY' in environment variables.
        """
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if self.api_key:
            self.app = FirecrawlApp(api_key=self.api_key)
        else:
            self.app = None

    def search(self, query, **kwargs):
        """
        Search the web using Firecrawl.
        Pass kwargs directly to the underlying SDK.
        """
        if not self.app:
            raise ValueError("FIRECRAWL_API_KEY not found.")
        
        return self.app.search(query, **kwargs)

    def scrape_url(self, url, params=None):
        """
        Scrape a specific URL.
        """
        if not self.app:
            raise ValueError("FIRECRAWL_API_KEY not found.")

        return self.app.scrape_url(url, params=params)
