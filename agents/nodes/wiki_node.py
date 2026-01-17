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
    from agents.validator import ContentValidator
    validator = ContentValidator()
    
    # Strategy: Use Wikipedia Search API to find the best matching page
    import requests
    
    page = None
    search_query = f"{movie_title} film"
    
    try:
        # 1. Search Wikipedia
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json"
        }
        headers = {
            "User-Agent": "CineMatrix-Bot/1.0 (contact@cinematrix.com)"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # Check for non-200 or HTML response
        if response.status_code != 200:
            logger.error(f"   Wikipedia API Status: {response.status_code}")
            
        data = response.json()
        
        candidates = []
        if "query" in data and "search" in data["query"]:
            # Add top 3 search results to candidates
            for item in data["query"]["search"][:3]:
                candidates.append(item["title"])
                
        # Also add direct title and (film) suffix as fallbacks
        if movie_title not in candidates:
            candidates.append(movie_title)
        if f"{movie_title} (film)" not in candidates:
            candidates.append(f"{movie_title} (film)")
            
        logger.info(f"   🔍 Wikipedia Candidates: {candidates}")

        # 2. Try Candidates
        for title in candidates:
            p = client.get_page(title)
            if p and p.exists():
                # Intelligent Verification
                summary = p.summary[0:2000]
                if validator.validate(summary, movie_title, "wikipedia"):
                    page = p
                    logger.info(f"   ✅ Verified page: '{title}'")
                    break
                else:
                    logger.info(f"   Skipping page '{title}' - failed validation.")

    except Exception as e:
        logger.error(f"   Wikipedia search failed: {e}")
    
    if not page:
        logger.warning(f"   Page not found.")
        return {"signals": []}

    # Validated Page Found
    
    # 1. Extract Sections (Recursive)
    parsed_sections = []
    def extract_sections(sections, level=1):
        for s in sections:
            if s.text.strip(): # Only include sections with text
                parsed_sections.append({
                    "title": s.title,
                    "content": s.text[:5000], # Reasonable limit
                    "level": level
                })
            extract_sections(s.sections, level + 1)
            
    extract_sections(page.sections)
    
    # 2. Update Movie Document
    from backend.database.client import MongoDBClient
    from bson import ObjectId
    
    db_client = MongoDBClient()
    db = db_client.get_db()
    movie_id = state["movie_id"] # Internal ID
    
    # Resolve ID
    try:
        if ObjectId.is_valid(movie_id):
            query = {"_id": ObjectId(movie_id)}
        else:
            query = {"movie_id": movie_id}
    except:
        query = {"movie_id": movie_id}
        
    db.movies.update_one(
        query,
        {"$set": {
            "wikipedia": {
                "page_title": page.title,
                "url": page.fullurl,
                "summary": page.summary[:2000],
                "sections": parsed_sections
            }
        }},
        upsert=True
    )
    
    logger.info(f"   ✅ Saved Wikipedia data ({len(parsed_sections)} sections) for {movie_title}")

    # 3. Return Signal for Sentiment Analysis
    summary = page.summary[0:2000]
    signal: SourceSentiment = {
        "source": "wikipedia",
        "text": summary,
        "url": page.fullurl,
        "metadata": {
            "title": page.title
        }
    }
    
    return {"signals": [signal]}
