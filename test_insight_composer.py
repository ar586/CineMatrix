
import unittest
from unittest.mock import MagicMock, patch
from agents.reasoning.schema import Hypothesis
from agents.insight.insight_composer import InsightComposer

class TestInsightComposer(unittest.TestCase):
    
    @patch("agents.insight.insight_composer.MongoDBClient")
    def test_compose_controversy(self, MockDB):
        # Setup Mock DB
        mock_collection = MockDB.return_value.get_db.return_value.insights
        
        # Setup Hypothesis
        hypothesis = Hypothesis(
            summary="Potential Controversy",
            confidence=0.8,
            trigger_signals=["sudden_hype", "sentiment_drop"],
            reasoning="Hype + Drop = Bad.",
            supporting_evidence=[
                {"signal": {"metadata": {"related_events": [{"type": "news"}]}}}
            ]
        )
        
        composer = InsightComposer()
        insights = composer.compose_and_store([hypothesis], "tt1")
        
        print("\n--- Insight Composition ---")
        print(f"Title: {insights[0].title}")
        print(f"Type: {insights[0].insight_type}")
        print(f"Visual: {insights[0].recommended_visual.component}")
        
        self.assertEqual(insights[0].insight_type, "controversy")
        self.assertEqual(insights[0].severity, "high")
        self.assertEqual(insights[0].recommended_visual.component, "line_chart")
        self.assertTrue(mock_collection.insert_one.called)

    @patch("agents.insight.insight_composer.MongoDBClient")
    def test_compose_polarization(self, MockDB):
        mock_collection = MockDB.return_value.get_db.return_value.insights
        
        hypothesis = Hypothesis(
            summary="Divisive",
            confidence=0.7,
            trigger_signals=["aspect_polarization"],
            reasoning="Split opinion.",
            supporting_evidence=[]
        )
        
        composer = InsightComposer()
        insights = composer.compose_and_store([hypothesis], "tt1")
        
        print(f"Visual (Polarization): {insights[0].recommended_visual.component}")
        self.assertEqual(insights[0].recommended_visual.component, "bar_chart")

if __name__ == "__main__":
    unittest.main()
