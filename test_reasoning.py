
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from agents.signals.schema import Signal
from agents.reasoning.event_correlation import EventCorrelation
from agents.reasoning.cross_signal_reasoning import CrossSignalReasoning

class TestReasoningAgents(unittest.TestCase):
    
    @patch("agents.reasoning.event_correlation.MongoDBClient")
    def test_event_correlation(self, MockDB):
        # Setup Signals
        signal = Signal(
            signal_type="sentiment_drop",
            movie_id="tt1",
            date="2026-01-05",
            severity="high",
            score=0.8,
            description="Big Drop"
        )
        
        # Setup Mock DB Events
        mock_db = MockDB.return_value.get_db.return_value
        # Event on Jan 4th (1 day before)
        mock_db.movie_events.find.return_value = [
            {
                "_id": "evt1",
                "movie_id": "tt1",
                "event_type": "news",
                "description": "Director Interview",
                "date": datetime(2026, 1, 4)
            }
        ]
        
        agent = EventCorrelation()
        enriched = agent.correlate([signal], "tt1")
        
        print("\n--- Event Correlation ---")
        related = enriched[0].metadata.get("related_events", [])
        print(f"Related Events: {related}")
        
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]["description"], "Director Interview")

    def test_cross_signal_synthesis(self):
        # Setup Signals: Controversy Pattern
        signals = [
            Signal(
                signal_type="sudden_hype",
                movie_id="tt1",
                date="2026-01-05",
                severity="high",
                score=0.9,
                description="Volume Exploded"
            ),
            Signal(
                signal_type="sentiment_drop",
                movie_id="tt1",
                date="2026-01-05", # Same day
                severity="high",
                score=0.7,
                description="Sentiment Crashed"
            )
        ]
        
        agent = CrossSignalReasoning()
        hypotheses = agent.synthesize(signals)
        
        print("\n--- Hypothesis Synthesis ---")
        for h in hypotheses:
            print(f"Hypothesis: {h.summary}")
            print(f"Reasoning: {h.reasoning}")
            
        self.assertTrue(any("Controversy" in h.summary for h in hypotheses))
        self.assertEqual(len(hypotheses), 1)

if __name__ == "__main__":
    unittest.main()
