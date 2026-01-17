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
    from backend.database.client import MongoDBClient
    from backend.database.dedup import bulk_upsert_youtube_videos
    from backend.database.similarity import find_similar_youtube_video
    movie_title = state["movie_title"]
    logger.info(f"🎥 [YouTube Agent] Activated for: {movie_title}")

    # 1. Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
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

    # 4. Filter (Intelligent Validator)
    from agents.validator import ContentValidator
    validator = ContentValidator()
    
    selected_indices = []
    for i, item in enumerate(raw_videos):
        snippet = item["snippet"]
        content = f"Title: {snippet['title']}\nChannel: {snippet['channelTitle']}\nDescription: {snippet['description'][:500]}"
        
        if validator.validate(content, movie_title, "youtube_video"):
             selected_indices.append(i)
             
    if not selected_indices:
        logger.warning("   All YouTube videos failed intelligent validation.")
        return {"signals": []}

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
            
            # Prepare Video Object for DB
            video_doc = {
                "movie_id": state["movie_id"],
                "video_id": vid_id,
                "video_type": "review", # Assumption based on query
                "title": snippet['title'],
                "channel": snippet['channelTitle'],
                "channel_id": snippet.get("channelId"),
                "url": f"https://youtube.com/watch?v={vid_id}",
                "published_at": snippet["publishedAt"], # Should technically parse this
                "description": snippet['description'],
                "stats": {
                    "views": 0, # Not fetching stats in this basic search
                    "likes": 0,
                    "comment_count": 0
                }
            }
            
            # Deduplication Check
            db_client = MongoDBClient()
            db = db_client.get_db()
            
            similar_vid_id = find_similar_youtube_video(db, state["movie_id"], snippet['title'])
            if similar_vid_id and similar_vid_id != vid_id:
                logger.info(f"   ⏭️  Skipping similar YouTube video: {snippet['title'][:50]}... (Matched {similar_vid_id})")
                continue

            # Using bulk upsert
            bulk_upsert_youtube_videos(db, [video_doc])
            logger.info(f"   ✅ Saved YouTube video {vid_id} to DB")

    return {"signals": signals}
