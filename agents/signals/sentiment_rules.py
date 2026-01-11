
from typing import List
from agents.signals.schema import Signal
from backend.database.models import DailyMovieSentiment

class SentimentRules:
    def detect_signals(self, history: List[DailyMovieSentiment]) -> List[Signal]:
        """
        Analyze daily sentiment history to detect drops and mismatches.
        History should be sorted by date (ascending).
        """
        signals = []
        if len(history) < 2:
            return signals

        current = history[-1]
        previous = history[-2]
        
        # 1. Sentiment Drop
        # Drop of > 0.3 on a -1 to 1 scale is significant
        drop_threshold = 0.3
        delta = current.overall_sentiment - previous.overall_sentiment
        
        if delta < -drop_threshold:
            signals.append(Signal(
                signal_type="sentiment_drop",
                movie_id=current.movie_id,
                date=current.date,
                severity="high" if delta < -0.5 else "medium",
                score=abs(delta),
                metadata={
                    "previous_sentiment": previous.overall_sentiment,
                    "current_sentiment": current.overall_sentiment,
                    "drop": delta
                },
                description=f"Significant sentiment drop of {round(delta, 2)} detected."
            ))

        # 2. Attention-Sentiment Mismatch
        # High volume but negative sentiment
        # Define high volume relative to history or static threshold?
        # Static for MVP: > 50 posts/videos and sentiment < -0.2
        total_volume = (current.volume.reddit_posts or 0) + (current.volume.youtube_videos or 0)
        
        if total_volume > 20 and current.overall_sentiment < -0.2:
            signals.append(Signal(
                signal_type="attention_mismatch",
                movie_id=current.movie_id,
                date=current.date,
                severity="medium",
                score=abs(current.overall_sentiment), # correlation strength
                metadata={
                    "volume": total_volume,
                    "sentiment": current.overall_sentiment
                },
                description="High attention despite negative sentiment."
            ))
            
        return signals
