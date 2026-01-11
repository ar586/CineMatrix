
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class Signal(BaseModel):
    signal_type: str  # e.g., "sentiment_drop", "sudden_hype"
    movie_id: str
    date: str
    severity: str  # low, medium, high
    score: float   # 0.0 to 1.0 indicating strength of signal
    metadata: Dict[str, Any] = {}
    description: str
    detected_at: datetime = datetime.utcnow()
