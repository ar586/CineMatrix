"""
Visualization Data Resolver
Converts LLM-generated data_query descriptions into actual numerical data.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VisualizationDataResolver:
    """
    Resolves data_query descriptions into actual database queries and formats
    the results for frontend chart consumption.
    """
    
    def __init__(self, db):
        self.db = db
    
    def resolve_data(self, movie_id: str, chart_type: str, data_query: str) -> List[Dict[str, Any]]:
        """
        Convert data_query description into actual numerical data.
        
        Args:
            movie_id: Movie identifier
            chart_type: Type of chart (line, bar, pie, radar, etc.)
            data_query: LLM-generated description of what data to fetch
            
        Returns:
            List of data points formatted for the chart type
        """
        try:
            # Parse the query intent
            query_lower = data_query.lower() if data_query else ""
            
            # Match query to appropriate data fetcher
            if "sentiment" in query_lower and "timeline" in query_lower:
                return self._fetch_sentiment_timeline(movie_id)
            elif "platform" in query_lower or "discussion" in query_lower:
                return self._fetch_platform_breakdown(movie_id)
            elif "aspect" in query_lower:
                return self._fetch_aspect_scores(movie_id)
            elif chart_type == "line":
                # Default for line charts: sentiment timeline
                return self._fetch_sentiment_timeline(movie_id)
            elif chart_type in ["bar", "pie"]:
                # Default for bar/pie: platform breakdown
                return self._fetch_platform_breakdown(movie_id)
            elif chart_type == "radar":
                # Default for radar: aspect scores
                return self._fetch_aspect_scores(movie_id)
            else:
                # Generic fallback
                return self._generate_fallback_data(movie_id, chart_type)
                
        except Exception as e:
            logger.error(f"Error resolving data for {movie_id}: {e}")
            return self._generate_fallback_data(movie_id, chart_type)
    
    def _fetch_sentiment_timeline(self, movie_id: str) -> List[Dict[str, Any]]:
        """Fetch daily sentiment data for line charts"""
        try:
            sentiments = list(self.db.daily_movie_sentiments.find(
                {"movie_id": movie_id}
            ).sort("date", 1).limit(30))
            
            if not sentiments:
                logger.warning(f"No sentiment timeline data for {movie_id}")
                return []
            
            return [
                {
                    "date": s.get("date", "Unknown"),
                    "sentiment": round(s.get("overall_sentiment", 0), 2)
                }
                for s in sentiments
            ]
        except Exception as e:
            logger.error(f"Error fetching sentiment timeline: {e}")
            return []
    
    def _fetch_platform_breakdown(self, movie_id: str) -> List[Dict[str, Any]]:
        """Fetch platform discussion counts for bar/pie charts"""
        try:
            # Aggregate source sentiments by platform
            pipeline = [
                {"$match": {"movie_id": movie_id}},
                {"$group": {
                    "_id": "$source",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            
            results = list(self.db.source_sentiments.aggregate(pipeline))
            
            if not results:
                logger.warning(f"No platform data for {movie_id}")
                return []
            
            # Format for charts
            return [
                {
                    "platform": r["_id"].capitalize(),
                    "name": r["_id"].capitalize(),  # For pie charts
                    "discussions": r["count"],
                    "value": r["count"]  # For pie charts
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error fetching platform breakdown: {e}")
            return []
    
    def _fetch_aspect_scores(self, movie_id: str) -> List[Dict[str, Any]]:
        """Fetch aspect scores for radar charts"""
        try:
            # Get latest daily sentiment with aspect summary
            sentiment = self.db.daily_movie_sentiments.find_one(
                {"movie_id": movie_id},
                sort=[("date", -1)]
            )
            
            if not sentiment or "aspect_summary" not in sentiment:
                logger.warning(f"No aspect data for {movie_id}")
                return []
            
            aspects = sentiment.get("aspect_summary", {})
            
            return [
                {
                    "aspect": aspect.replace("_", " ").title(),
                    "score": round(float(score), 2) if score is not None else 0.0
                }
                for aspect, score in aspects.items()
                if score is not None  # Skip None values
            ]
        except Exception as e:
            logger.error(f"Error fetching aspect scores: {e}")
            return []
    
    def _generate_fallback_data(self, movie_id: str, chart_type: str) -> List[Dict[str, Any]]:
        """Generate basic data when query parsing fails"""
        try:
            if chart_type == "line":
                return self._fetch_sentiment_timeline(movie_id)
            elif chart_type in ["bar", "pie"]:
                return self._fetch_platform_breakdown(movie_id)
            elif chart_type == "radar":
                return self._fetch_aspect_scores(movie_id)
            else:
                logger.warning(f"No fallback for chart type: {chart_type}")
                return []
        except Exception as e:
            logger.error(f"Error generating fallback data: {e}")
            return []
