
from typing import List
from agents.signals.schema import Signal
from backend.database.models import DailyMovieSentiment

class AspectRules:
    def detect_signals(self, history: List[DailyMovieSentiment]) -> List[Signal]:
        """
        Analyze history for aspect polarization or divergence.
        """
        signals = []
        if not history:
            return signals

        current = history[-1]
        
        # 1. Aspect Divergence
        # e.g. Acting is Great (+0.8) vs Story is Terrible (-0.8)
        if current.aspect_summary:
            scores = current.aspect_summary.model_dump(exclude_none=True).values()
            if scores:
                max_score = max(scores)
                min_score = min(scores)
                spread = max_score - min_score
                
                if spread > 1.2: # Significant divergence (e.g. +0.6 and -0.7)
                    signals.append(Signal(
                        signal_type="aspect_polarization",
                        movie_id=current.movie_id,
                        date=current.date,
                        severity="medium",
                        score=spread / 2.0,
                        metadata={
                            "spread": spread,
                            "max_aspect": max_score,
                            "min_aspect": min_score
                        },
                        description="Significant divergence between aspect sentiments."
                    ))

        return signals
