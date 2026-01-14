import json
import logging
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from backend import config
from agents.state import AgentState, SourceSentiment
from backend.datasources.youtube.client import YouTubeClient

logger = logging.getLogger(__name__)

def youtube_agent_node(state: AgentState):
    """
    LangGraph node for YouTube data fetching.
    """
    movie_title = state["movie_title"]
    logger.info(f"🎥 [YouTube Agent] Activated for: {movie_title}")

    # 1. Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.7
    )

    # 2. Generate Queries
    query_prompt = f"""
    You are a Video Analyst. Generate 3 YouTube search queries for critical reviews of "{movie_title}".
    Avoid generic trailers. Focus on video essays and deep dives.
    Output strictly a JSON list of strings.
    """
    
    queries = [f"{movie_title} video essay", f"{movie_title} review"]
    # try:
    #     response = llm.invoke([HumanMessage(content=query_prompt)])
    #     text = response.content.replace("```json", "").replace("```", "").strip()
    #     queries = json.loads(text)
    # except Exception as e:
    #     logger.error(f"   Failed to generate queries: {e}")
    #     queries = [f"{movie_title} movie review", f"{movie_title} video essay"]

    # 3. Fetch Data
    yt_client = YouTubeClient()
    raw_videos = []
    seen_ids = set()
    
    if yt_client.youtube:
        for q in queries:
            try:
                # Search, limit 3 per query
                res = yt_client.search_videos(q, max_results=3)
                if "items" in res:
                    for item in res["items"]:
                        vid_id = item["id"].get("videoId")
                        if vid_id and vid_id not in seen_ids:
                            raw_videos.append(item)
                            seen_ids.add(vid_id)
            except Exception as e:
                logger.warning(f"   Search error for '{q}': {e}")
    
    if not raw_videos:
        logger.warning("   No videos found.")
        return {"signals": []}

    # 4. Filter (LLM)
    candidates = []
    for i, item in enumerate(raw_videos):
        snippet = item["snippet"]
        candidates.append(f"INDEX {i}: Title: {snippet['title']} | Channel: {snippet['channelTitle']} | Desc: {snippet['description'][:150]}")
    
    candidates_str = "\n".join(candidates)
    
    filter_prompt = f"""
    Select the most insightful video reviews for "{movie_title}".
    Ignore clickbait or simple reactions.
    CANDIDATES:
    {candidates_str}
    
    Output strictly a JSON list of integer INDICES. Example: [0, 1]
    """
    
    selected_indices = list(range(len(raw_videos))) # Default all
    # try:
    #     response = llm.invoke([HumanMessage(content=filter_prompt)])
    #     text = response.content.replace("```json", "").replace("```", "").strip()
    #     selected_indices = json.loads(text)
    # except Exception:
    #     pass # Fallback to all

    # 5. Format
    signals: List[SourceSentiment] = []
    for idx in selected_indices:
        if idx < len(raw_videos):
            item = raw_videos[idx]
            snippet = item["snippet"]
            vid_id = item["id"]["videoId"]
            signal: SourceSentiment = {
                "source": "youtube",
                "text": f"{snippet['title']}\n\n{snippet['description']}",
                "url": f"https://youtube.com/watch?v={vid_id}",
                "metadata": {
                    "video_id": vid_id,
                    "channel": snippet["channelTitle"],
                    "published_at": snippet["publishedAt"]
                }
            }
            signals.append(signal)

    return {"signals": signals}
