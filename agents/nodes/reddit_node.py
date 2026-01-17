import json
import logging
from typing import List, Dict
from datetime import datetime, timezone
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
    4. SAVES RAW POSTS to DB (deduplicated).
    """
    from backend.database.client import MongoDBClient
    from backend.database.dedup import bulk_upsert_reddit_posts
    from backend.database.similarity import find_similar_reddit_post
    
    movie_title = state["movie_title"]
    movie_id = state["movie_id"]
    logger.info(f"🤖 [Reddit Agent] Activated for: {movie_title}")

    # 1. Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
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

    # 4. Filter for Relevance using Intelligent Validator
    from agents.validator import ContentValidator
    validator = ContentValidator()
    
    selected_indices = []
    
    # We validate each post briefly
    for i, post in enumerate(raw_posts):
        # Construct a representative snippet
        content = f"Title: {post.title}\nSubreddit: {post.subreddit.display_name}\nContent: {post.selftext[:500]}"
        
        if validator.validate(content, movie_title, "reddit_post"):
            selected_indices.append(i)
        
        # Stop if we have enough
        if len(selected_indices) >= 5:
            break
            
    if not selected_indices:
        # Fallback if strict validation fails for all (should be rare for 'relevant' search)
        # We might take top 2 just in case, or return empty.
        # Let's trust the validator for now but log warning.
        logger.warning("   All Reddit posts failed intelligent validation.")
        return {"signals": []}

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
            
            # Fetch top comments from the post
            comments = []
            try:
                # Replace "MoreComments" objects to get actual comments
                post.comments.replace_more(limit=0)
                
                # Get all top-level comments and sort by score
                top_comments = sorted(
                    post.comments.list(),
                    key=lambda c: c.score if hasattr(c, 'score') else 0,
                    reverse=True
                )[:5]  # Get top 5 comments
                
                for comment in top_comments:
                    if hasattr(comment, 'body') and hasattr(comment, 'score'):
                        comments.append({
                            "comment_id": comment.id,
                            "text": comment.body,
                            "score": comment.score,
                            "created_at": datetime.fromtimestamp(comment.created_utc, timezone.utc)
                        })
                
                logger.info(f"   Fetched {len(comments)} comments for post {post.id}")
            except Exception as e:
                logger.warning(f"   Failed to fetch comments for post {post.id}: {e}")
            
            # Create formatted post object for DB
            reddit_post_doc = {
                "movie_id": movie_id,
                "post_id": post.id,
                "subreddit": post.subreddit.display_name,
                "title": post.title,
                "selftext": post.selftext,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "num_comments": post.num_comments,
                "created_at": datetime.fromtimestamp(post.created_utc, timezone.utc),
                "comments": comments  # Now populated with actual comments
            }
            
            # Deduplication Check
            db_client = MongoDBClient()
            db = db_client.get_db()
            
            similar_post_id = find_similar_reddit_post(db, movie_id, post.title)
            if similar_post_id and similar_post_id != post.id:
                logger.info(f"   ⏭️  Skipping similar Reddit post: {post.title[:50]}... (Matched {similar_post_id})")
                continue

            # Using bulk upsert from dedicated function
            bulk_upsert_reddit_posts(db, [reddit_post_doc])
            
            logger.info(f"   ✅ Saved Reddit post {post.id} to DB")

    return {"signals": signals}
