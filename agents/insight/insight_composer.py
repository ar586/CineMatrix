
import json
from typing import List
from datetime import datetime
from agents.reasoning.schema import Hypothesis
from backend.database.client import MongoDBClient
from backend.database.models import (
    Insight, Evidence, RecommendedVisual, GeneratorInfo, RelatedEvent
)
from backend.llm.client import LLMService
from backend.database.similarity import find_similar_insight

class InsightComposer:
    def __init__(self):
        self.db_client = MongoDBClient()
        self.llm = LLMService()

    def compose_and_store(self, hypotheses: List[Hypothesis], movie_id: str) -> List[Insight]:
        """
        Converts hypotheses into Insight objects and stores them in DB using LLM to generate narrative.
        """
        insights = []
        db = self.db_client.get_db()
        collection = db.insights
        
        for hypothesis in hypotheses:
            
            # --- LLM Refinement ---
            prompt = f"""
            You are a professional movie data analyst.
            Transform this hypothesis into a final Insight Report for a dashboard.
            
            Hypothesis: "{hypothesis.summary}"
            Reasoning: "{hypothesis.reasoning}"
            Confidence: {hypothesis.confidence}
            
            Output JSON with:
            - "title": A catchy, professional headline (max 8 words).
            - "summary": A concise, executive paragraph explaining the insight (max 50 words).
            - "insight_type": One of [controversy, trend, reception_shift, polarization, anomaly].
            - "severity": [low, medium, high].
            - "visual_component": One of [line_chart, bar_chart, pie_chart, heatmap].
            - "visual_x_axis": Suggested X-axis label.
            - "visual_y_axes": List of strings for Suggested Y-axis metrics.
            """
            
            llm_res = self.llm.generate_json(prompt)
            
            # Use LLM results or fallback to hypothesis data
            title = llm_res.get("title", hypothesis.summary)
            summary = llm_res.get("summary", hypothesis.reasoning)
            insight_type = llm_res.get("insight_type", "anomaly")
            severity = llm_res.get("severity", "medium")
            
            # Visual Recommendation
            visual = RecommendedVisual(
                component=llm_res.get("visual_component", "line_chart"),
                x=llm_res.get("visual_x_axis", "date"),
                y=llm_res.get("visual_y_axes", ["daily_sentiment"])
            )

            # Construct Evidence (from hypothesis)
            related_events = []
            for ev_item in hypothesis.supporting_evidence:
                signal_data = ev_item.get("signal", {})
                meta = signal_data.get("metadata", {})
                if "related_events" in meta:
                    for re in meta["related_events"]:
                        related_events.append(RelatedEvent(
                            event_type=re.get("type", "unknown"),
                            event_date=re.get("date")
                        ))

            evidence = Evidence(
                related_events=related_events,
                sentiment_change=None, 
                interest_change=None
            )

            # Create Insight Object
            insight = Insight(
                movie_id=movie_id,
                insight_type=insight_type,
                severity=severity,
                title=title,
                summary=summary,
                evidence=evidence,
                recommended_visual=visual,
                confidence=hypothesis.confidence,
                generated_by=GeneratorInfo(
                    agent="insight_composer_llm",
                    version="2.0"
                ),
                generated_at=datetime.utcnow()
            )
            
            # Deduplication Check (before storing)
            existing_id = find_similar_insight(db, movie_id, title, summary)
            if existing_id:
                print(f"Skipping duplicate insight: {title} (Matched {existing_id})")
                continue
                
            # Store
            try:
                # Exclude None values to prevent _id: null error
                insight_dict = insight.model_dump(by_alias=True, exclude_none=True)
                collection.insert_one(insight_dict)
                print(f"Stored insight: {title}")
                insights.append(insight)
            except Exception as e:
                print(f"Error storing insight: {e}")

        return insights
