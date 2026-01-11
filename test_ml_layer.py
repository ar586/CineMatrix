
import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock transformers and scipy before importing models
sys.modules["transformers"] = MagicMock()
sys.modules["scipy.special"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["torch"] = MagicMock()

# Now we can import the classes, but we need to patch the internal usage
from backend.ml.sentiment_model import RobertaSentiment
from backend.ml.aspect_model import DebertaAspect
from agents.signals.sentiment_signal import SentimentSignal

class TestMLLayer(unittest.TestCase):
    def test_roberta_sentiment(self):
        # Mock the tokenizer and model inside RobertaSentiment
        with patch("backend.ml.sentiment_model.AutoTokenizer") as MockTokenizer, \
             patch("backend.ml.sentiment_model.AutoModelForSequenceClassification") as MockModel, \
             patch("backend.ml.sentiment_model.softmax") as mock_softmax, \
             patch("backend.ml.sentiment_model.np") as mock_np:
            
            # Setup mock returns
            mock_model_instance = MockModel.from_pretrained.return_value
            # Output of model is a tuple (logits,)
            mock_model_instance.return_value = [MagicMock()] 
            
            # Mock softmax return
            mock_softmax.return_value = [0.1, 0.2, 0.7] # neg, neu, pos
            
            # Mock numpy argsort to return indices sorted ascending by score
            # If scores are [0.1, 0.2, 0.7], argsort is [0, 1, 2]
            mock_np.argsort.return_value = [0, 1, 2] 
            
            model = RobertaSentiment()
            label, score, confidence = model.predict("This movie is amazing")
            
            print(f"Roberta Predict: Label={label}, Score={score}, Conf={confidence}")
            self.assertEqual(label, "positive")
            self.assertGreater(score, 0) # Should be positive

    def test_deberta_aspect(self):
        with patch("backend.ml.aspect_model.pipeline") as mock_pipeline:
            mock_classifier = mock_pipeline.return_value
            mock_classifier.return_value = {
                "labels": ["acting", "story"],
                "scores": [0.95, 0.4]
            }
            
            model = DebertaAspect()
            aspects = model.extract_aspects("The acting was great but story was meh")
            
            print(f"Deberta Aspects: {aspects}")
            self.assertEqual(aspects["acting"], 0.95)
            self.assertEqual(aspects["story"], 0.4)

    def test_sentiment_signal_integration(self):
        # Mock the ML models class instantiation inside SentimentSignal
        with patch("agents.signals.sentiment_signal.RobertaSentiment") as MockRoberta, \
             patch("agents.signals.sentiment_signal.DebertaAspect") as MockDeberta:
            
            mock_roberta = MockRoberta.return_value
            mock_roberta.predict.return_value = ("negative", -0.8, 0.9)
            
            mock_deberta = MockDeberta.return_value
            mock_deberta.extract_aspects.return_value = {"ending": 0.9, "acting": 0.2}
            
            signal = SentimentSignal()
            result = signal.analyze("Terrible ending", "reddit", {})
            
            print(f"Signal Result: {result}")
            self.assertEqual(result["sentiment"]["label"], "negative")
            self.assertEqual(result["sentiment"]["score"], -0.8)
            # Aspect sentiment = relevance * overall_score
            # ending: 0.9 * -0.8 = -0.72
            self.assertEqual(result["aspects"]["ending"], -0.72)

if __name__ == "__main__":
    unittest.main()
