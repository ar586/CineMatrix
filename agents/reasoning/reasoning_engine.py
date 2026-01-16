import logging
import json
from typing import List, Optional
from datetime import datetime
from backend.llm.client import LLMService
from backend.database.models import DailyMovieSentiment
from agents.reasoning.schema import Hypothesis

logger = logging.getLogger(__name__)

class ReasoningEngine:
    def __init__(self):
        self.llm = LLMService()

    def analyze_daily_update(self, daily: DailyMovieSentiment) -> List[Hypothesis]:
        """
        Analyzes the daily sentiment aggregation to spot trends/anomalies.
        """
        try:
            # 1. Construct Prompt Context from Daily Data
            context = f"""
            Movie: {daily.movie_id}
            Date: {daily.date}
            Overall Sentiment: {daily.overall_sentiment} (Confidence: {daily.confidence})
            Volatility: {daily.volatility}
            Volume: Reddit={daily.volume.reddit_posts}, YouTube={daily.volume.youtube_videos}
            
            Source Breakdown:
            {daily.source_breakdown.model_dump_json()}
            
            Aspect Summary:
            {daily.aspect_summary.model_dump_json()}
            """
            
            prompt = f"""
            You are a Movie Market Analyst. Analyze the following daily data:
            {context}
            
            Identify 1-3 key insights or hypotheses about the movie's current reception.
            Focus on:
            - Significant divergence between sources (e.g. Critics vs Fans).
            - Unusual volatility or spikes in volume.
            - Specific aspects (e.g. Acting, Plot) driving the sentiment.
            
            Output strictly a JSON list of objects with:
            - "summary": One-line title of the insight.
            - "reasoning": Detailed explanation.
            - "confidence": Float 0.0-1.0.
            - "type": "trend", "anomaly", "polarization".
            """
            
            # 2. Call LLM
            response = self.llm.generate_json(prompt)
            
            # 3. Parse to Hypothesis objects
            hypotheses = []
            if isinstance(response, list):
                for item in response:
                    hypotheses.append(Hypothesis(
                        summary=item.get("summary", "New Insight"),
                        reasoning=item.get("reasoning", ""),
                        confidence=item.get("confidence", 0.5),
                        trigger_signals=[item.get("type", "general")],
                        supporting_evidence=[] # No raw signals here, just agg stats
                    ))
            
            return hypotheses

        except Exception as e:
            logger.error(f"Reasoning Engine failed: {e}")
            return []
