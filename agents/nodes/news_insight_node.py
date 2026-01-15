import logging
from datetime import datetime, timezone
from agents.state import AgentState
from backend.database.client import MongoDBClient
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

def news_insight_node(state: AgentState):
    """
    LangGraph node for extracting insights from news articles using LLM.
    Analyzes scraped articles and stores structured insights in MongoDB.
    """
    movie_title = state["movie_title"]
    movie_id = state["movie_id"]
    articles = state.get("news_articles", [])
    
    if not articles:
        logger.warning("   No news articles to process")
        return {}
    
    logger.info(f"🧠 [News Insight] Analyzing {len(articles)} articles for: {movie_title}")
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3)
        db_client = MongoDBClient()
        db = db_client.get_db()
        
        # Filter out similar articles using similarity detection
        from backend.database.similarity import find_similar_news_article
        
        filtered_articles = []
        for article in articles:
            similar_url = find_similar_news_article(db, movie_id, article['title'], threshold=0.90)
            if similar_url:
                logger.info(f"   ⏭️  Skipping similar article: {article['title'][:60]}...")
            else:
                filtered_articles.append(article)
        
        logger.info(f"   Filtered {len(articles)} articles → {len(filtered_articles)} unique articles")
        articles = filtered_articles
        
        if not articles:
            logger.info("   No unique articles to process after similarity filtering")
            return {}
        
        processed_articles = []
        
        for article in articles:
            try:
                # Truncate content for LLM (max 2000 chars)
                content = article['content'][:2000]
                
                # LLM prompt for insight extraction
                prompt = f"""Analyze this news article about the movie "{movie_title}":

Title: {article['title']}
Content: {content}

Extract:
1. **Key Insights** (3-5 bullet points, each max 100 chars)
2. **Category** (choose ONE: box_office, controversy, awards, production, reviews, cast_news, general)
3. **Sentiment** (choose ONE: positive, negative, neutral)
4. **Relevance Score** (0.0-1.0, how relevant is this to the movie?)

Format your response EXACTLY as:
INSIGHTS:
- [insight 1]
- [insight 2]
- [insight 3]
CATEGORY: [category]
SENTIMENT: [sentiment]
RELEVANCE: [score]"""

                response = llm.invoke(prompt)
                parsed = self._parse_llm_response(response.content)
                
                # Create news article document
                news_doc = {
                    "movie_id": movie_id,
                    "title": article['title'],
                    "url": article['url'],
                    "source": article['source'],
                    "published_date": None,  # TODO: Extract from content if possible
                    "content_snippet": article['content'][:500],
                    "full_content": article['content'],
                    "insights": parsed['insights'],
                    "category": parsed['category'],
                    "sentiment": parsed['sentiment'],
                    "relevance_score": parsed['relevance'],
                    "fetched_at": datetime.now(timezone.utc)
                }
                
                processed_articles.append(news_doc)
                
            except Exception as e:
                logger.warning(f"   Failed to process article {article['url']}: {e}")
                continue
        
        # Store in MongoDB
        if processed_articles:
            from backend.database.dedup import bulk_upsert_news_articles
            bulk_upsert_news_articles(db, processed_articles)
            logger.info(f"   ✅ Saved {len(processed_articles)} news articles to DB (with deduplication)")
        
        return {}
        
    except Exception as e:
        logger.error(f"   ❌ News insight extraction failed: {e}")
        return {"errors": [str(e)]}
    
    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM response into structured data"""
        insights = []
        category = "general"
        sentiment = "neutral"
        relevance = 0.5
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('INSIGHTS:'):
                current_section = 'insights'
            elif line.startswith('CATEGORY:'):
                category = line.split(':', 1)[1].strip().lower()
            elif line.startswith('SENTIMENT:'):
                sentiment = line.split(':', 1)[1].strip().lower()
            elif line.startswith('RELEVANCE:'):
                try:
                    relevance = float(line.split(':', 1)[1].strip())
                except:
                    relevance = 0.5
            elif current_section == 'insights' and line.startswith('-'):
                insight = line[1:].strip()
                if insight:
                    insights.append(insight)
        
        return {
            'insights': insights[:5],  # Max 5
            'category': category,
            'sentiment': sentiment,
            'relevance': relevance
        }
