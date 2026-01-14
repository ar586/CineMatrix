import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from backend import config
from agents.state import AgentState, SourceSentiment
from backend.datasources.wikipedia.client import WikipediaClient

logger = logging.getLogger(__name__)

def wiki_agent_node(state: AgentState):
    """
    LangGraph node for Wikipedia data fetching.
    """
    movie_title = state["movie_title"]
    logger.info(f"📖 [Wiki Agent] Activated for: {movie_title}")

    client = WikipediaClient()
    
    # Strategy: Try direct title, then (film) suffix
    candidates = [movie_title, f"{movie_title} (film)"]
    page = None
    
    for title in candidates:
        p = client.get_page(title)
        if p and p.exists():
            # Minimal verification: Check if it has "film" or "movie" in summary
            if "film" in p.summary.lower() or "movie" in p.summary.lower():
                page = p
                break
    
    if not page:
        logger.warning(f"   Page not found.")
        return {"signals": []}

    # Format Signal
    summary = page.summary[0:2000] # Limit length
    signal: SourceSentiment = {
        "source": "wikipedia",
        "text": summary,
        "url": page.fullurl,
        "metadata": {
            "title": page.title
        }
    }
    
    return {"signals": [signal]}
