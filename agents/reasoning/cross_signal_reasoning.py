
import json
from typing import List
import logging
from agents.signals.schema import Signal
from agents.reasoning.schema import Hypothesis
from backend.llm.client import LLMService

logger = logging.getLogger(__name__)

class CrossSignalReasoning:
    def __init__(self):
        self.llm = LLMService()

    def synthesize(self, signals: List[Signal]) -> List[Hypothesis]:
        """
        Combines signals to form hypotheses using LLM.
        """
        if not signals:
            return []

        # 1. Prepare Signal Context
        signals_json = [s.model_dump() for s in signals]
        signal_descriptions = "\n".join([f"- [{s.signal_type}] {s.description} (Source: {s.metadata.get('source', 'unknown')})" for s in signals])

        # 2. Construct Prompt
        prompt = f"""
        You are an advanced Market Intelligence AI for the movie industry.
        Analyze the following 'Signals' detected from social media and data sources:
        
        {signal_descriptions}
        
        Detailed Data:
        {json.dumps(signals_json, default=str)}
        
        Task:
        Identify correlations, anomalies, or emerging narratives.
        Formulate specific hypotheses about the audience reception or market trend.
        
        Output a JSON array of objects with these keys:
        - "summary": Short title of the insight.
        - "confidence": Float between 0.0 and 1.0.
        - "trigger_signals": List of signal_type strings involved.
        - "reasoning": Detailed explanation of the correlation.
        """
        
        # 3. Call LLM
        response = self.llm.generate_json(prompt)
        
        # 4. Parse Response
        hypotheses = []
        if isinstance(response, list):
            for item in response:
                try:
                    # Map back to original signal objects for evidence
                    triggered_types = item.get("trigger_signals", [])
                    evidence = []
                    for sig in signals:
                         if sig.signal_type in triggered_types:
                             evidence.append({"signal": sig.model_dump()})
                    
                    hypotheses.append(Hypothesis(
                        summary=item.get("summary", "Unknown Insight"),
                        confidence=item.get("confidence", 0.5),
                        trigger_signals=triggered_types,
                        reasoning=item.get("reasoning", ""),
                        supporting_evidence=evidence
                    ))
                except Exception as e:
                    logger.error(f"Failed to parse hypothesis item: {e}")
        
        return hypotheses

