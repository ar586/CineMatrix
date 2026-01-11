
import unittest
from datetime import datetime, timedelta
from backend.database.models import DailyMovieSentiment, Volume, Aspects, SourceBreakdown
from agents.signals.sentiment_rules import SentimentRules
from agents.signals.trend_rules import TrendRules
from agents.signals.aspect_rules import AspectRules

class TestSignalAgents(unittest.TestCase):
    def setUp(self):
        # Create base history
        self.movie_id = "tt1"
        self.history = []
        
        # Day 1: Normal
        self.history.append(DailyMovieSentiment(
            movie_id=self.movie_id,
            date="2026-01-01",
            overall_sentiment=0.8,
            confidence=0.9,
            volume=Volume(reddit_posts=10, youtube_videos=2),
            aspect_summary=Aspects(acting=0.8, story=0.8),
            processed_at=datetime.utcnow()
        ))
        
    def test_sentiment_drop(self):
        # Day 2: Big Drop
        self.history.append(DailyMovieSentiment(
            movie_id=self.movie_id,
            date="2026-01-02",
            overall_sentiment=0.2, # Drop of 0.6
            confidence=0.9,
            volume=Volume(),
            processed_at=datetime.utcnow()
        ))
        
        rules = SentimentRules()
        signals = rules.detect_signals(self.history)
        
        print(f"Sentiment Signals: {[s.signal_type for s in signals]}")
        self.assertTrue(any(s.signal_type == "sentiment_drop" for s in signals))
        self.assertEqual(signals[0].severity, "high")

    def test_sudden_hype(self):
        # Day 2: Massive Volume Spike
        self.history.append(DailyMovieSentiment(
            movie_id=self.movie_id,
            date="2026-01-02",
            overall_sentiment=0.8,
            confidence=0.9,
            volume=Volume(reddit_posts=100, youtube_videos=20), # 120 total vs 12
            processed_at=datetime.utcnow()
        ))
        
        rules = TrendRules()
        signals = rules.detect_signals(self.history)
        
        print(f"Trend Signals: {[s.signal_type for s in signals]}")
        self.assertTrue(any(s.signal_type == "sudden_hype" for s in signals))
        self.assertTrue("1000%" in signals[0].description) # 12 -> 120 is 10x (900% increase? Logic says ratio > 2.0)

    def test_aspect_polarization(self):
        # Day 1 with polarization
        polarized_day = DailyMovieSentiment(
            movie_id=self.movie_id,
            date="2026-01-01",
            overall_sentiment=0.0,
            confidence=0.9,
            aspect_summary=Aspects(acting=0.9, story=-0.9), # Spread 1.8
            processed_at=datetime.utcnow()
        )
        
        rules = AspectRules()
        signals = rules.detect_signals([polarized_day])
        
        print(f"Aspect Signals: {[s.signal_type for s in signals]}")
        self.assertTrue(any(s.signal_type == "aspect_polarization" for s in signals))

if __name__ == "__main__":
    unittest.main()
