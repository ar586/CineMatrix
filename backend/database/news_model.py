
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated, Union
from datetime import datetime

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class NewsArticle(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    title: str
    url: str
    source: str = Field(..., description="Domain name of the source")
    published_date: Optional[datetime] = None
    
    content_snippet: str = Field(..., description="First 500 chars of content")
    full_content: Optional[str] = None  # Store full markdown content
    
    insights: List[str] = Field(default_factory=list, description="Key points extracted by LLM")
    category: str = Field(default="general", description="box_office, controversy, awards, production, reviews, cast_news")
    sentiment: str = Field(default="neutral", description="positive, negative, neutral")
    relevance_score: float = Field(default=0.5, description="0-1 score of relevance")
    
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
