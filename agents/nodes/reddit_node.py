import json
import logging
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend import config
from agents.state import AgentState, SourceSentiment
from backend.datasources.reddit.client import RedditClient

logger = logging.getLogger(__name__)

def reddit_agent_node(state: AgentState):
    """
    LangGraph node for Reddit data fetching.
    1. Generates queries.
    2. Fetches from Reddit.
    3. Filters for relevance.
    """
    movie_title = state["movie_title"]
    logger.info(f"🤖 [Reddit Agent] Activated for: {movie_title}")

    # 1. Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.7
    )

    # 2. Generate Queries
    query_prompt = f"""
    You are a Researcher. Generate 3 specific search queries to find Reddit discussions about the movie "{movie_title}".
    Focus on:
    - General discussions
    - Critical reviews
    - Plot analysis
    
    Output strictly a JSON list of strings. Example: ["{movie_title} discussion", "{movie_title} review"]
    """
    
    queries = [f"{movie_title} discussion", f"{movie_title} review"]
    # try:
    #     response = llm.invoke([HumanMessage(content=query_prompt)])
    #     text = response.content.replace("```json", "").replace("```", "").strip()
    #     queries = json.loads(text)
    #     logger.info(f"   Generated queries: {queries}")
    # except Exception as e:
    #     logger.error(f"   Failed to generate queries: {e}")
    #     queries = [f"{movie_title} movie discussion"] # Fallback

    # 3. Fetch Data (Tool Execution)
    reddit = RedditClient().get_instance()
    raw_posts = []
    seen_ids = set()
    
    if reddit:
        for q in queries:
            try:
                # Search 'all' subreddits, limit 5 per query
                results = reddit.subreddit("all").search(f'"{q}"', limit=5, sort="relevance")
                for post in results:
                    if post.id not in seen_ids:
                        raw_posts.append(post)
                        seen_ids.add(post.id)
            except Exception as e:
                logger.warning(f"   Search error for '{q}': {e}")
    
    if not raw_posts:
        return {"signals": [], "errors": ["No Reddit posts found"]}
        
    logger.info(f"   Fetched {len(raw_posts)} raw posts. Filtering...")

    # 4. Filter for Relevance (LLM)
    # create a simplified list for the LLM to review
    candidates = []
    for i, post in enumerate(raw_posts):
        candidates.append(f"INDEX {i}: Title: {post.title} | Subreddit: {post.subreddit.display_name} | Content Preview: {post.selftext[:200]}...")
    
    candidates_str = "\n".join(candidates)
    
    filter_prompt = f"""
    You are a Content Curator. Select the most relevant and substantial Reddit discussions about "{movie_title}" from the list below.
    Ignore low-effort posts, memes, or unrelated topics.
    Select up to 5 best posts.
    
    CANDIDATES:
    {candidates_str}
    
    Output strictly a JSON list of integer INDICES. Example: [0, 2, 5]
    """
    
    selected_indices = list(range(min(5, len(raw_posts))))
    # try:
    #     response = llm.invoke([HumanMessage(content=filter_prompt)])
    #     text = response.content.replace("```json", "").replace("```", "").strip()
    #     selected_indices = json.loads(text)
    #     logger.info(f"   Selected indices: {selected_indices}")
    # except Exception as e:
    #     logger.error(f"   Filtering failed: {e}")
    #     # Fallback: take top 3
    #     selected_indices = list(range(min(3, len(raw_posts))))

    # 5. Format Signals
    signals: List[SourceSentiment] = []
    for idx in selected_indices:
        if idx < len(raw_posts):
            post = raw_posts[idx]
            signal: SourceSentiment = {
                "source": "reddit",
                "text": f"{post.title}\n\n{post.selftext}",
                "url": f"https://reddit.com{post.permalink}",
                "metadata": {
                    "post_id": post.id,
                    "subreddit": post.subreddit.display_name,
                    "upvotes": post.score,
                    "comments": post.num_comments
                }
            }
            signals.append(signal)

    return {"signals": signals}
