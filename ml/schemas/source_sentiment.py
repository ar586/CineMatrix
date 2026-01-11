
from pydantic import BaseModel
from typing import Optional, Dict

class SentimentInput(BaseModel):
    text: str
    source: str
    source_ref: Dict[str, str]
    engagement: Dict[str, int]
    movie_id: str

class SentimentOutput(BaseModel):
    label: str
    score: float
    confidence: float
    aspects: Dict[str, float]
