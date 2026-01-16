import os
from firecrawl import FirecrawlApp
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

logger = logging.getLogger(__name__)

class FirecrawlClient:
    """Client for Firecrawl web scraping"""
    
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.client = FirecrawlApp(api_key=self.api_key)
        from backend import config
        model_name = getattr(config, "LLM_MODEL", "models/gemma-3-27b-it")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
    
    def generate_search_queries(self, movie_title: str, cast: list = None) -> list[str]:
        """
        Generate diverse search queries for a movie using LLM.
        Includes: news, box office, controversies, cast news, awards, production updates
        """
        cast_str = ", ".join(cast[:3]) if cast else "the cast"
        
        prompt = f"""Generate 5 diverse Google search queries to find recent news articles about the movie "{movie_title}".
        
Include queries covering:
1. General news and updates
2. Box office performance
3. Controversies or scandals (related to the movie or cast: {cast_str})
4. Awards and nominations
5. Production updates or behind-the-scenes news

Return ONLY the search queries, one per line, without numbering or explanations."""

        try:
            response = self.llm.invoke(prompt)
            queries = [q.strip() for q in response.content.strip().split('\n') if q.strip()]
            logger.info(f"Generated {len(queries)} search queries for {movie_title}")
            return queries[:5]  # Limit to 5
        except Exception as e:
            logger.error(f"Failed to generate queries with LLM: {e}")
            # Fallback queries
            return [
                f'"{movie_title}" news',
                f'"{movie_title}" box office',
                f'"{movie_title}" controversy',
                f'"{movie_title}" {cast_str} news',
                f'"{movie_title}" awards'
            ]
    
    def search_and_scrape(self, query: str, limit: int = 2) -> list[dict]:
        """
        Search Google and scrape top results using Firecrawl.
        Returns list of scraped pages with title, url, and markdown content.
        """
        try:
            # Use Firecrawl's search feature
            search_results = self.client.search(query, limit=limit)
            
            scraped_pages = []
            # Iterate over 'web' attribute (List[SearchResultWeb]) if present
            results_list = getattr(search_results, 'web', []) or []
            
            scraped_pages = []
            for result in results_list:
                try:
                    # Scrape each URL
                    # Use scrape() instead of scrape_url(), pass formats as kwarg
                    scrape_result = self.client.scrape(
                        result.url,
                        formats=['markdown']
                    )
                    
                    if scrape_result and hasattr(scrape_result, 'markdown') and scrape_result.markdown:
                        scraped_pages.append({
                            'title': getattr(result, 'title', 'Untitled'),
                            'url': result.url,
                            'content': scrape_result.markdown,
                            'source': self._extract_domain(result.url)
                        })
                except Exception as e:
                    # getattr(result, 'url', 'unknown') just in case
                    url_str = getattr(result, 'url', 'unknown')
                    logger.warning(f"Failed to scrape {url_str}: {e}")
                    continue
            
            return scraped_pages
        except Exception as e:
            logger.error(f"Search and scrape failed for query '{query}': {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
