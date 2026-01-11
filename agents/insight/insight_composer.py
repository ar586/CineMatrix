
from typing import List
from datetime import datetime
from agents.reasoning.schema import Hypothesis
from backend.database.client import MongoDBClient
from backend.database.models import (
    Insight, Evidence, RecommendedVisual, GeneratorInfo, RelatedEvent
)

class InsightComposer:
    def __init__(self):
        self.db_client = MongoDBClient()

    def compose_and_store(self, hypotheses: List[Hypothesis], movie_id: str) -> List[Insight]:
        """
        Converts hypotheses into Insight objects and stores them in DB.
        """
        insights = []
        db = self.db_client.get_db()
        collection = db.insights
        
        for hypothesis in hypotheses:
            # 1. Determine Narrative / Insight Type
            # Map hypothesis trigger signals to insight type/title
            insight_type = "anomaly"
            title = hypothesis.summary
            severity = "medium"
            
            triggers = set(hypothesis.trigger_signals)
            
            if "sentiment_drop" in triggers:
                if "sudden_hype" in triggers:
                    insight_type = "controversy"
                    severity = "high"
                    # Title is likely already set well by CrossSignalReasoning ("Potential Controversy")
                else:
                    insight_type = "reception_shift"
                    title = "Sudden Sentinel Drop Detected"
            elif "aspect_polarization" in triggers:
                insight_type = "polarization"
                title = "Audience Divided on Key Aspects"
            elif "sudden_hype" in triggers:
                insight_type = "trend"
                title = "Viral Volume Spike"

            # 2. visual Recommendation
            # Default to line chart for trends
            visual = RecommendedVisual(
                component="line_chart",
                x="date",
                y=["daily_sentiment", "volume"]
            )
            
            if insight_type == "polarization":
                visual = RecommendedVisual(
                    component="bar_chart",
                    x="aspect",
                    y=["score"]
                )

            # 3. Construct Evidence
            # Extract related events from hypothesis supporting evidence
            related_events = []
            for ev_item in hypothesis.supporting_evidence:
                # ev_item might comprise the Signal object dump
                # check if signal metadata has related_events
                signal_data = ev_item.get("signal", {})
                meta = signal_data.get("metadata", {})
                
                # If 'related_events' in metadata
                if "related_events" in meta:
                    for re in meta["related_events"]:
                        related_events.append(RelatedEvent(
                            event_type=re.get("type", "unknown"),
                            event_date=re.get("date") # might be missing or need formatting
                        ))

            evidence = Evidence(
                related_events=related_events,
                # We could extract sentiment change quantifiers from signal scores/metadata if needed
                sentiment_change=None, 
                interest_change=None
            )

            # 4. Create Insight Object
            insight = Insight(
                movie_id=movie_id,
                insight_type=insight_type,
                severity=severity,
                title=title,
                summary=hypothesis.reasoning,
                evidence=evidence,
                recommended_visual=visual,
                confidence=hypothesis.confidence,
                generated_by=GeneratorInfo(
                    agent="insight_composer",
                    version="1.0"
                ),
                generated_at=datetime.utcnow()
            )
            
            insights.append(insight)
            
            # 5. Store in DB
            try:
                collection.insert_one(insight.model_dump(by_alias=True))
                print(f"Stored insight: {title}")
            except Exception as e:
                print(f"Error storing insight: {e}")

        return insights
