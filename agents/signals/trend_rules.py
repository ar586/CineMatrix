
from typing import List
from agents.signals.schema import Signal
from backend.database.models import DailyMovieSentiment

class TrendRules:
    def detect_signals(self, history: List[DailyMovieSentiment]) -> List[Signal]:
        """
        Analyze history for sudden hype/trend spikes.
        """
        signals = []
        if len(history) < 2:
            return signals

        current = history[-1]
        previous = history[-2]
        
        # 1. Sudden Hype (Volume Spike)
        # 200% increase in volume
        current_vol = (current.volume.reddit_posts or 0) + (current.volume.youtube_videos or 0)
        prev_vol = (previous.volume.reddit_posts or 0) + (previous.volume.youtube_videos or 0)
        
        # Avoid division by zero
        if prev_vol == 0:
            if current_vol > 10: # Spiked from 0 to something significant
                ratio = 10.0 # treating as 10x
            else:
                ratio = 1.0
        else:
            ratio = current_vol / prev_vol
            
        if ratio > 2.0: # 100% increase
            signals.append(Signal(
                signal_type="sudden_hype",
                movie_id=current.movie_id,
                date=current.date,
                severity="high" if ratio > 5.0 else "medium",
                score=min(1.0, ratio / 10.0), # normalize roughly
                metadata={
                    "previous_volume": prev_vol,
                    "current_volume": current_vol,
                    "ratio": round(ratio, 2)
                },
                description=f"Volume spiked by {round(ratio * 100)}%."
            ))
            
        return signals
