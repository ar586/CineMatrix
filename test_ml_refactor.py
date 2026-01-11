
import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock dependencies
sys.modules["transformers"] = MagicMock()
sys.modules["scipy.special"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["torch"] = MagicMock()

# Patch DB Client
from ml.pipelines.sentiment_worker import SentimentWorker
from ml.pipelines.sentiment_engine import SentimentEngine

class TestMLRefactor(unittest.TestCase):
    
    def test_discussion_builder(self):
        from ml.pipelines.discussion_builder import DiscussionBuilder
        builder = DiscussionBuilder()
        item = {
            "title": "Title",
            "selftext": "Body",
            "comments": ["C1", "C2"]
        }
        text = builder.build_text(item, "reddit")
        self.assertEqual(text, "Title Body C1 C2")

    @patch("ml.pipelines.sentiment_engine.RobertaSentiment")
    @patch("ml.pipelines.sentiment_engine.DebertaAspect")
    def test_sentiment_engine(self, MockDeberta, MockRoberta):
        # Setup mocks
        mock_roberta = MockRoberta.return_value
        mock_roberta.predict.return_value = ("positive", 0.9, 0.95)
        
        mock_deberta = MockDeberta.return_value
        mock_deberta.extract_aspects.return_value = {"acting": 0.8}
        
        # Reset singleton logic if needed (or just rely on mock being instantiated)
        # Since SentimentEngine is a singleton using __new__, patching class inside the module 
        # *might* not affect if it was already imported/instantiated?
        # Actually, python modules are cached. But `from ml.pipelines.sentiment_engine` imports the class.
        # Patching `ml.pipelines.sentiment_engine.RobertaSentiment` patches the name correctly.
        
        # Force re-instantiation or clear instance
        SentimentEngine._instance = None
        engine = SentimentEngine()
        
        output = engine.analyze("some text")
        
        self.assertEqual(output.label, "positive")
        self.assertEqual(output.score, 0.9)
        self.assertEqual(output.aspects["acting"], 0.72) # 0.8 * 0.9

    @patch("ml.pipelines.sentiment_worker.MongoDBClient")
    @patch("ml.pipelines.sentiment_worker.SentimentEngine")
    def test_sentiment_worker(self, MockEngine, MockDB):
        # Setup Engine Mock
        mock_engine_instance = MockEngine.return_value
        mock_output = MagicMock()
        mock_output.label = "negative"
        mock_output.score = -0.5
        mock_output.confidence = 0.8
        mock_output.aspects = {"story": -0.4}
        mock_engine_instance.analyze.return_value = mock_output
        
        # Setup DB Mock
        mock_db_instance = MockDB.return_value
        mock_collection = MagicMock()
        mock_db_instance.get_db.return_value.source_sentiments = mock_collection
        
        worker = SentimentWorker()
        
        item = {"id": "123", "title": "Bad Movie"}
        worker.process_item(item, "reddit", "tt000")
        
        # Verify DB insert
        self.assertTrue(mock_collection.insert_one.called)
        call_arg = mock_collection.insert_one.call_args[0][0]
        self.assertEqual(call_arg["sentiment"]["label"], "negative")
        self.assertEqual(call_arg["aspects"]["story"], -0.4)

if __name__ == "__main__":
    unittest.main()
