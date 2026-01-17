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
        
        # Deduplicate, Validate, and Filter
        from agents.validator import ContentValidator
        validator = ContentValidator()
        
        seen_urls = set()
        unique_articles = []
        
        for article in all_articles:
            if article['url'] not in seen_urls:
                # Validate relevance
                # Firecrawl often returns 'markdown' or 'content'
                content_snippet = article.get('markdown', '') or article.get('description', '') or article.get('title', '')
                
                if validator.validate(content_snippet[:1000], movie_title, "news_article"):
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
        
        logger.info(f"   ✅ validated {len(unique_articles)} relevant articles from {len(all_articles)} raw results.")
        
        # Store articles in state for news insight node
        return {"news_articles": unique_articles}
        
    except Exception as e:
        logger.error(f"   ❌ Firecrawl failed: {e}")
        return {"news_articles": [], "errors": [str(e)]}
