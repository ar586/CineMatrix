"""
Visualization Agent Node
Generates and caches diverse visualizations including charts, text content, and news cards.
Runs as part of the daily update pipeline.
"""
import logging
import hashlib
import json
from typing import Dict
from datetime import datetime, timezone

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.database.client import MongoDBClient
from backend.llm.client import LLMService
from agents.state import AgentState

logger = logging.getLogger(__name__)

def visualization_agent_node(state: AgentState) -> AgentState:
    """
    Generate and cache visualizations for a movie.
    Creates diverse content: charts, text cards, news highlights, controversies, etc.
    """
    movie_id = state.get("movie_id")
    movie_title = state.get("movie_title")
    
    logger.info(f"🎨 Generating visualizations for {movie_title}")
    
    try:
        generator = VisualizationGenerator()
        generator.generate_and_cache(movie_id, movie_title)
        logger.info(f"✅ Visualizations cached for {movie_title}")
    except Exception as e:
        logger.error(f"❌ Visualization generation failed for {movie_title}: {e}")
        state.setdefault("errors", []).append(f"Visualization generation: {str(e)}")
    
    return state


class VisualizationGenerator:
    """Generates and caches visualizations using LLM"""
    
    def __init__(self):
        self.db_client = MongoDBClient()
        self.llm = LLMService()
    
    def generate_and_cache(self, movie_id: str, movie_title: str):
        """Generate visualizations and save to database"""
        db = self.db_client.get_db()
        if db is None:
            raise ConnectionError("Database connection failed")
        
        # Aggregate all available data
        context = self._aggregate_context(db, movie_id, movie_title)
        
        # Calculate data hash for cache invalidation
        data_hash = self._calculate_data_hash(context)
        
        # Check if we need to regenerate
        existing = db.visualization_components.find_one({
            "movie_id": movie_id,
            "data_hash": data_hash
        })
        
        if existing:
            logger.info(f"Using cached visualizations (data unchanged)")
            return
        
        # Generate new visualizations using LLM
        visualizations = self._llm_generate(context, movie_title)
        
        # Clear old visualizations for this movie
        db.visualization_components.delete_many({"movie_id": movie_id})
        
        # Save new visualizations
        for viz in visualizations:
            db.visualization_components.insert_one({
                "movie_id": movie_id,
                "component_id": viz["id"],
                "type": viz["type"],
                "priority": viz.get("priority", 5),
                "spec": viz["component"],
                "data_hash": data_hash,
                "generated_at": datetime.now(timezone.utc),
                "reuse_count": 0
            })
        
        logger.info(f"Saved {len(visualizations)} visualizations to cache")
    
    def _aggregate_context(self, db, movie_id: str, movie_title: str) -> Dict:
        """Gather all relevant data for visualization generation"""
        
        # Get sentiment data
        sentiments = list(db.daily_sentiments.find(
            {"movie_id": movie_id}
        ).sort("date", -1).limit(30))
        
        # Get insights
        insights = list(db.insights.find(
            {"movie_id": movie_id}
        ).sort("generated_at", -1).limit(10))
        
        # Get news articles
        news = list(db.news_articles.find(
            {"movie_id": movie_id}
        ).sort("fetched_at", -1).limit(10))
        
        # Get source sentiments for interesting discussions
        discussions = list(db.source_sentiments.find(
            {"movie_id": movie_id}
        ).sort("created_at", -1).limit(50))
        
        # Get movie metadata
        movie = db.movies.find_one({"_id": movie_id})
        
        return {
            "movie_id": movie_id,
            "movie_title": movie_title,
            "metadata": movie or {},
            "sentiments": sentiments,
            "insights": insights,
            "news": news,
            "discussions": discussions,
            "stats": self._calculate_stats(sentiments, discussions)
        }
    
    def _calculate_stats(self, sentiments, discussions):
        """Calculate aggregate statistics"""
        if not sentiments:
            return {}
        
        return {
            "avg_sentiment": sum(s.get("overall_sentiment", 0) for s in sentiments) / len(sentiments),
            "total_volume": sum(
                s.get("volume", 0) if isinstance(s.get("volume"), int) else 
                sum(s.get("volume", {}).values()) if isinstance(s.get("volume"), dict) else 0
                for s in sentiments
            ),
            "discussion_count": len(discussions),
            "platforms": list(set(d.get("source") for d in discussions if d.get("source")))
        }
    
    def _calculate_data_hash(self, context: Dict) -> str:
        """Calculate hash of data for cache invalidation"""
        # Hash based on key data points
        hash_data = {
            "sentiment_count": len(context.get("sentiments", [])),
            "news_count": len(context.get("news", [])),
            "discussion_count": len(context.get("discussions", [])),
            "latest_sentiment": str(context.get("sentiments", [{}])[0].get("date")) if context.get("sentiments") else None
        }
        return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def _llm_generate(self, context: Dict, movie_title: str) -> list:
        """Use LLM to generate diverse visualizations"""
        
        stats = context.get("stats", {})
        news_titles = [n.get("title", "") for n in context.get("news", [])[:5]]
        insights_summary = [i.get("title", "") for i in context.get("insights", [])[:5]]
        
        prompt = f"""You are creating an engaging dashboard for the movie "{movie_title}".

Available Data:
- Average Sentiment: {stats.get('avg_sentiment', 0):.2f}
- Total Discussions: {stats.get('total_volume', 0)}
- Platforms: {', '.join(stats.get('platforms', []))}
- Recent News: {', '.join(news_titles) if news_titles else 'None'}
- Key Insights: {', '.join(insights_summary) if insights_summary else 'None'}

Create 10-15 DIVERSE and INTERESTING components. Mix different types:

1. **Charts/Graphs** (30%): Standard visualizations (line, bar, pie, radar, heatmap)
2. **Text Content Cards** (40%): Controversial takes, breaking news, trivia, cast updates
3. **Custom Visualizations** (30%): Creative infographics, timelines, comparisons

For each component, return JSON:
{{
  "id": "unique_id",
  "type": "chart|text_card|custom",
  "priority": 1-10 (lower = more important),
  "component": {{
    // For charts:
    "chart_type": "line|bar|pie|radar|heatmap",
    "title": "Engaging Title",
    "description": "What this shows",
    "data_query": "What data to fetch",
    "styling": {{"color_scheme": "sentiment-based|vibrant|monochrome"}}
    
    // For text cards:
    "card_type": "news|controversy|trivia|update",
    "title": "Attention-grabbing headline",
    "content": "The actual text content (2-3 sentences max)",
    "source": "Where this info came from",
    "styling": {{"theme": "alert|info|highlight"}}
    
    // For custom:
    "custom_type": "timeline|comparison|meter",
    "title": "Creative title",
    "description": "How to interpret this",
    "layout_hint": "Visual layout description"
  }}
}}

Be CREATIVE and ENGAGING! Think about:
- What would make users say "wow, I didn't know that!"
- What controversies or debates exist?
- What's trending about this movie right now?
- What interesting patterns exist in the data?

Return a JSON array of 10-15 components.
"""
        
        try:
            result = self.llm.generate_json(prompt)
            
            if isinstance(result, list) and len(result) > 0:
                logger.info(f"LLM generated {len(result)} visualizations")
                return result
            else:
                logger.warning("LLM returned invalid format, using fallback")
                return self._fallback_visualizations(context)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}, using fallback")
            return self._fallback_visualizations(context)
    
    def _fallback_visualizations(self, context: Dict) -> list:
        """Fallback visualizations if LLM fails"""
        stats = context.get("stats", {})
        
        return [
            {
                "id": "sentiment_trend",
                "type": "chart",
                "priority": 1,
                "component": {
                    "chart_type": "line",
                    "title": "Sentiment Timeline",
                    "description": "Audience sentiment over the past 30 days",
                    "data_query": "daily_sentiments",
                    "styling": {"color_scheme": "sentiment-based"}
                }
            },
            {
                "id": "platform_breakdown",
                "type": "chart",
                "priority": 2,
                "component": {
                    "chart_type": "bar",
                    "title": "Discussion by Platform",
                    "description": f"Conversations across {len(stats.get('platforms', []))} platforms",
                    "data_query": "platform_volume",
                    "styling": {"color_scheme": "vibrant"}
                }
            },
            {
                "id": "quick_stats",
                "type": "text_card",
                "priority": 3,
                "component": {
                    "card_type": "info",
                    "title": "At a Glance",
                    "content": f"Average sentiment: {stats.get('avg_sentiment', 0):.2f}/1.0. Total discussions: {stats.get('total_volume', 0)}. Active on {len(stats.get('platforms', []))} platforms.",
                    "source": "Aggregated data",
                    "styling": {"theme": "info"}
                }
            }
        ]
