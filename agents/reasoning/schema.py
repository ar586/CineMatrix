
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Hypothesis(BaseModel):
    summary: str
    confidence: float
    trigger_signals: List[str] # List of Signal types/IDs
    reasoning: str
    supporting_evidence: List[Dict[str, Any]] # e.g. [{"type": "event", "description": "..."}]
    created_at: datetime = datetime.utcnow()
