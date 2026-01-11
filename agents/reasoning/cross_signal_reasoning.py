
from typing import List
from agents.signals.schema import Signal
from agents.reasoning.schema import Hypothesis

class CrossSignalReasoning:
    def synthesize(self, signals: List[Signal]) -> List[Hypothesis]:
        """
        Combines signals to form hypotheses.
        """
        hypotheses = []
        
        # Group signals by date proximity? Or just analyze the set?
        # For MVP, look for co-occurrence in the passed list (assuming generic time window passed)
        
        signal_types = [s.signal_type for s in signals]
        
        # Pattern 1: Controversy (Hype + Drop + [Polarization])
        if "sudden_hype" in signal_types and "sentiment_drop" in signal_types:
            # Find the specific signals
            hype = next(s for s in signals if s.signal_type == "sudden_hype")
            drop = next(s for s in signals if s.signal_type == "sentiment_drop")
            
            hypotheses.append(Hypothesis(
                summary="Potential Controversy or Scandal",
                confidence=0.8,
                trigger_signals=["sudden_hype", "sentiment_drop"],
                reasoning=f"Volume spiked ({hype.description}) while sentiment crashed ({drop.description}). This usually indicates a controversial event.",
                supporting_evidence=[
                   {"signal": hype.model_dump()},
                   {"signal": drop.model_dump()}
                ]
            ))

        # Pattern 2: Viral Hit (Hype + Positive/High Sentiment)
        # We don't have a "Positive Sentiment" signal from SignalAgents yet, 
        # but we can infer if Hype exists and NO sentiment drop exists, 
        # OR we check the metadata of the Hype signal if it carries sentiment info?
        # The Signal agent logic for Hype didn't capture sentiment.
        # Ideally, we'd look at the raw data or have a "Positive Surge" signal.
        # For now, let's skip or assume logic: Hype + No Drop = Likely Good? 
        # Risky. Let's stick to explicit signals.
        
        # Pattern 3: Divisive Reception (Polarization + Mismatch/Drop)
        if "aspect_polarization" in signal_types:
            polar = next(s for s in signals if s.signal_type == "aspect_polarization")
            hypotheses.append(Hypothesis(
                summary="Divisive Audience Reception",
                confidence=0.7,
                trigger_signals=["aspect_polarization"],
                reasoning=f"Audience is split on specific aspects: {polar.description}",
                supporting_evidence=[
                    {"signal": polar.model_dump()}
                ]
            ))
            
        return hypotheses
