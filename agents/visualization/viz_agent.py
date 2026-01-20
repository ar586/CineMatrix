"""
Dynamic Visualization Agent
Analyzes all available movie data and generates creative visualizations using LLM.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from backend.database.client import MongoDBClient
from backend.llm.client import LLMService
from agents.visualization.data_resolver import VisualizationDataResolver

logger = logging.getLogger(__name__)

class VisualizationAgent:
    """
    Intelligent agent that analyzes movie data and generates dynamic visualizations.
    Uses LLM to determine the most insightful ways to present data.
    """
    
    def __init__(self, db=None, db_client=None, llm_service=None):
        self.db = db
        self._db_client = db_client
        self.llm = llm_service or LLMService()

    @property
    def db_client(self):
        if not self._db_client and not self.db:
            self._db_client = MongoDBClient()
        return self._db_client
    
    def aggregate_context(self, movie_id: str) -> Dict:
        """
        Aggregate all relevant data from database for analysis.
        Includes sentiment, volume, aspects, insights, news, metadata, and raw discussions.
        """
        db = self.db
        if db is None:
            db = self.db_client.get_db()
        
        # Validate database connection
        if db is None:
            logger.error("Database connection failed in VisualizationAgent")
            raise ConnectionError("Failed to connect to database. Please check MongoDB connection settings.")
        
        # Get sentiment data (last 30 days)
        sentiments = list(db.daily_movie_sentiments.find(
            {"movie_id": movie_id}
        ).sort("date", -1).limit(30))
        
        # Get source-specific sentiments (sample for raw data)
        source_sentiments = list(db.source_sentiments.find(
            {"movie_id": movie_id}
        ).sort("created_at", -1).limit(50))
        
        # Get insights
        insights = list(db.insights.find(
            {"movie_id": movie_id}
        ).sort("generated_at", -1).limit(10))
        
        # Get news articles
        news = list(db.news_articles.find(
            {"movie_id": movie_id}
        ).sort("fetched_at", -1).limit(10))
        
        # Get movie metadata
        movie = db.movies.find_one({"_id": movie_id})

        # Get trends data
        trends = db.google_trends.find_one({"movie_id": movie_id}, sort=[("ingested_at", -1)])
        
        # Calculate aggregated metrics
        context = {
            "movie_id": movie_id,
            "movie_title": movie.get("title", "Unknown") if movie else "Unknown",
            "metadata": {
                "budget": movie.get("budget", 0) if movie else 0,
                "revenue": movie.get("revenue", 0) if movie else 0,
                "imdb_rating": movie.get("imdb", {}).get("rating", 0) if movie else 0,
                "rt_score": movie.get("rotten_tomatoes", {}).get("critics_score", 0) if movie else 0,
                "genres": movie.get("genres", []) if movie else [],
            },
            "sentiment_data": {
                "timeline": [
                    {
                        "date": s.get("date"),
                        "sentiment": s.get("overall_sentiment", 0),
                        "volume": s.get("volume", 0) if isinstance(s.get("volume"), int) else 
                                 sum(s.get("volume", {}).values()) if isinstance(s.get("volume"), dict) else 0
                    }
                    for s in sentiments
                ],
                "avg_sentiment": sum(s.get("overall_sentiment", 0) for s in sentiments) / len(sentiments) if sentiments else 0,
                "total_volume": sum(
                    s.get("volume", 0) if isinstance(s.get("volume"), int) else 
                    sum(s.get("volume", {}).values()) if isinstance(s.get("volume"), dict) else 0
                    for s in sentiments
                ),
                "sentiment_volatility": self._calculate_volatility([s.get("overall_sentiment", 0) for s in sentiments]),
            },
            "aspect_data": self._aggregate_aspects(sentiments),
            "platform_breakdown": self._aggregate_by_platform(source_sentiments),
            "insights_summary": [
                {
                    "title": i.get("title"),
                    "type": i.get("insight_type"),
                    "severity": i.get("severity")
                }
                for i in insights
            ],
            "news_summary": [
                {
                    "title": n.get("title"),
                    "category": n.get("category"),
                    "sentiment": n.get("sentiment")
                }
                for n in news
            ],
            "raw_discussions": self._sample_discussions(source_sentiments, limit=5),
            "trends_data": trends or {}
        }
        
        return context
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate standard deviation as volatility measure"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _aggregate_aspects(self, sentiments: List[Dict]) -> Dict:
        """Aggregate aspect scores across all sentiment data"""
        aspect_totals = {}
        aspect_counts = {}
        
        for s in sentiments:
            aspects = s.get("aspect_summary", {})
            for aspect, score in aspects.items():
                aspect_totals[aspect] = aspect_totals.get(aspect, 0) + score
                aspect_counts[aspect] = aspect_counts.get(aspect, 0) + 1
        
        return {
            aspect: aspect_totals[aspect] / aspect_counts[aspect]
            for aspect in aspect_totals
        }
    
    def _aggregate_by_platform(self, source_sentiments: List[Dict]) -> Dict:
        """Aggregate sentiment and volume by platform"""
        platforms = {}
        
        for s in source_sentiments:
            source = s.get("source", "unknown")
            if source not in platforms:
                platforms[source] = {"count": 0, "total_sentiment": 0}
            
            platforms[source]["count"] += 1
            platforms[source]["total_sentiment"] += s.get("sentiment", {}).get("score", 0)
        
        return {
            platform: {
                "count": data["count"],
                "avg_sentiment": data["total_sentiment"] / data["count"] if data["count"] > 0 else 0
            }
            for platform, data in platforms.items()
        }
    
    def _sample_discussions(self, source_sentiments: List[Dict], limit: int = 5) -> List[Dict]:
        """Sample interesting discussions for context"""
        return [
            {
                "source": s.get("source"),
                "text": s.get("text", "")[:200],  # First 200 chars
                "sentiment": s.get("sentiment", {}).get("label", "neutral")
            }
            for s in source_sentiments[:limit]
        ]
    
    def generate_visualizations(self, movie_id: str, page: int = 1, limit: int = 5) -> Dict:
        """
        Serve pre-generated visualizations from cache only.
        Visualizations are generated in background by the daily update pipeline.
        """
        try:
            logger.info(f"DEBUG: VisualizationAgent.generate_visualizations - self.db: {self.db}")
            db = self.db
            if db is None:
                db = self.db_client.get_db()

            if db is None:
                logger.warning("Database connection unavailable")
                return self._empty_fallback_response(page)
            
            # Fetch cached visualizations
            cached = db.visualization_components.find(
                {"movie_id": movie_id}
            ).sort("priority", 1).skip((page - 1) * limit).limit(limit)
            
            cached_list = list(cached)
            
            # Check if we have any cached visualizations
            if not cached_list:
                logger.info(f"No cached visualizations found for {movie_id}")
                return self._no_data_response(page, movie_id)
            
            # NEW: Initialize data resolver
            resolver = VisualizationDataResolver(db)
            
            # Resolve actual data for each visualization
            visualizations_with_data = []
            for viz in cached_list:
                spec = viz.get("spec", {})
                chart_type = spec.get("chart_type")
                data_query = spec.get("data_query", "")
                viz_type = viz.get("type")
                
                # Only resolve data for chart types (not text cards)
                if chart_type and viz_type == "chart":
                    try:
                        resolved_data = resolver.resolve_data(movie_id, chart_type, data_query)
                        spec["data"] = resolved_data
                        
                        # Only include if we have meaningful data
                        if resolved_data and len(resolved_data) > 0:
                            visualizations_with_data.append(viz)
                            logger.info(f"✅ Resolved {len(resolved_data)} data points for {chart_type} chart")
                        else:
                            logger.info(f"⏭️  Skipping {chart_type} chart - no data available")
                    except Exception as e:
                        logger.error(f"Failed to resolve data for {chart_type}: {e}")
                        # Skip this visualization entirely
                else:
                    # Include text cards and other non-chart types
                    visualizations_with_data.append(viz)
            
            # Update cached_list to only include visualizations with data
            cached_list = visualizations_with_data
            
            # If no visualizations have data, return empty response
            if not cached_list:
                logger.info(f"No visualizations with data for {movie_id}")
                return self._no_data_response(page, movie_id)
            
            # Get total count for pagination (only count visualizations with data)
            total_count = len(visualizations_with_data)
            total_pages = (total_count + limit - 1) // limit
            
            return {
                "page": page,
                "total_pages": total_pages,
                "has_more": page < total_pages,
                "visualizations": [
                    {
                        "id": c["component_id"],
                        "type": c["type"],
                        "priority": c.get("priority", 5),
                        "component": c["spec"]
                    }
                    for c in cached_list
                ],
                "generated_at": cached_list[0]["generated_at"].isoformat() if cached_list else None,
                "cached": True
            }
            
        except Exception as e:
            logger.error(f"Error fetching cached visualizations: {e}")
            return self._empty_fallback_response(page)
    
    def _llm_generate_visualizations(self, context: Dict, page: int, limit: int) -> Dict:
        """Use LLM to generate creative visualizations"""
        
        prompt = f"""You are a data visualization expert analyzing movie sentiment data.

Movie: {context['movie_title']}
Average Sentiment: {context['sentiment_data']['avg_sentiment']:.2f}
Total Discussions: {context['sentiment_data']['total_volume']}
Volatility: {context['sentiment_data']['sentiment_volatility']:.2f}
Top Aspects: {list(context['aspect_data'].keys())[:3]}
Platforms: {list(context['platform_breakdown'].keys())}
Viral Trends: {context.get('trends_data', {}).get('related_queries', {}).get('rising', [])[:3]}
Top Regions: {context.get('trends_data', {}).get('interest_by_region', [])[:3]}

Generate {limit} creative visualizations for page {page}. For each:
1. Choose the most insightful chart type
2. Create a compelling title
3. Provide context/description
4. Specify data structure

Return JSON array with format:
[{{
  "id": "unique_id",
  "type": "statistic|chart|text_card",
  "priority": 1-10,
  "component": {{
    "chart_type": "line|bar|radar|heatmap|pie",
    "title": "Engaging Title",
    "content": "Narrative or key takeaway for text_card type",
    "description": "Context about what this shows",
    "data_query": "Description of what data to fetch",
    "styling": {{"color_scheme": "sentiment-based|vibrant|monochrome", "theme": "alert|info|highlight|default"}}
  }}
}}]

Be creative! Mix charts with narrative text cards. 
For every 2-3 charts, include a 'text_card' that synthesizes a key insight or interesting trend in 2-3 sentences.
Consider: sentiment journeys, platform comparisons, aspect radars, volume heatmaps."""

        try:
            result = self.llm.generate_json(prompt)
            
            if isinstance(result, list):
                return {
                    "page": page,
                    "total_pages": 6,  # Estimate
                    "has_more": page < 6,
                    "visualizations": result,
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return self._fallback_visualizations(context, page, limit)
                
        except Exception as e:
            logger.error(f"LLM visualization generation failed: {e}")
            return self._fallback_visualizations(context, page, limit)
    
    def _fallback_visualizations(self, context: Dict, page: int, limit: int) -> Dict:
        """Fallback visualizations if LLM fails"""
        fallback = [
            {
                "id": "sentiment_trend",
                "type": "chart",
                "priority": 1,
                "component": {
                    "chart_type": "line",
                    "title": "Sentiment Timeline",
                    "description": "Audience sentiment over the past 30 days",
                    "data": context["sentiment_data"]["timeline"]
                }
            },
            {
                "id": "platform_breakdown",
                "type": "chart",
                "priority": 2,
                "component": {
                    "chart_type": "bar",
                    "title": "Discussion by Platform",
                    "description": "Where people are talking about this movie",
                    "data": context["platform_breakdown"]
                }
            }
        ]
        
        start = (page - 1) * limit
        end = start + limit
        
        return {
            "page": page,
            "total_pages": 2,
            "has_more": page < 2,
            "visualizations": fallback[start:end],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _cache_components(self, movie_id: str, visualizations: Dict):
        """Save generated components to database for reuse"""
        db = self.db
        if db is None:
            db = self.db_client.get_db()
        
        for viz in visualizations.get("visualizations", []):
            try:
                db.visualization_components.update_one(
                    {
                        "movie_id": movie_id,
                        "component_id": viz["id"]
                    },
                    {
                        "$set": {
                            "type": viz["type"],
                            "spec": viz["component"],
                            "priority": viz.get("priority", 5),
                            "generated_at": datetime.now(timezone.utc)
                        },
                        "$inc": {"reuse_count": 1}
                    },
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Failed to cache component: {e}")
    
    def _format_cached_response(self, cached: List[Dict], page: int, limit: int, movie_id: str) -> Dict:
        """Format cached components as response"""
        return {
            "page": page,
            "total_pages": 6,
            "has_more": len(cached) == limit,
            "visualizations": [
                {
                    "id": c["component_id"],
                    "type": c["type"],
                    "priority": c.get("priority", 5),
                    "component": c["spec"]
                }
                for c in cached
            ],
            "cached_at": cached[0]["generated_at"].isoformat() if cached else None
        }
    
    def _empty_fallback_response(self, page: int) -> Dict:
        """Return empty but valid response when database is unavailable"""
        logger.warning("Returning empty fallback response due to database unavailability")
        return {
            "page": page,
            "total_pages": 0,
            "has_more": False,
            "visualizations": [],
            "error": "Database connection unavailable. Please check your connection settings."
        }
    
    def _no_data_response(self, page: int, movie_id: str) -> Dict:
        """Return response when no visualizations have been generated yet"""
        logger.info(f"No visualizations cached for {movie_id}")
        return {
            "page": page,
            "total_pages": 0,
            "has_more": False,
            "visualizations": [],
            "message": "Visualizations are being generated. Please check back after the next daily update.",
            "cached": False
        }
