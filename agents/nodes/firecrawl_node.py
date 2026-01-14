import logging
from agents.state import AgentState
from backend.datasources.firecrawl.client import FirecrawlClient

logger = logging.getLogger(__name__)

def firecrawl_agent_node(state: AgentState):
    """
    LangGraph node for Firecrawl news fetching.
    Generates search queries and scrapes relevant news articles.
    """
    movie_title = state["movie_title"]
    movie_id = state.get("movie_id")
    
    # Get cast info if available (for better query generation)
    cast = state.get("cast", [])
    
    logger.info(f"📰 [Firecrawl Agent] Activated for: {movie_title}")
    
    try:
        client = FirecrawlClient()
        
        # Generate diverse search queries
        queries = client.generate_search_queries(movie_title, cast)
        logger.info(f"   Generated {len(queries)} search queries")
        
        # Scrape articles for each query (2 per query = ~10 total articles)
        all_articles = []
        for query in queries:
            articles = client.search_and_scrape(query, limit=2)
            all_articles.extend(articles)
            logger.info(f"   Scraped {len(articles)} articles for: {query[:50]}...")
        
        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"   ✅ Total unique articles: {len(unique_articles)}")
        
        # Store articles in state for news insight node
        return {"news_articles": unique_articles}
        
    except Exception as e:
        logger.error(f"   ❌ Firecrawl failed: {e}")
        return {"news_articles": [], "errors": [str(e)]}
