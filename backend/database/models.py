
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated
from datetime import datetime

# Helper for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class Certification(BaseModel):
    US: Optional[str] = None
    IN: Optional[str] = None

class Crew(BaseModel):
    director: Optional[str] = None
    writers: List[str] = Field(default_factory=list)
    producers: List[str] = Field(default_factory=list)

class IMDBData(BaseModel):
    rating: Optional[float] = None
    votes: Optional[int] = None
    last_updated: Optional[datetime] = None

class RottenTomatoesData(BaseModel):
    critics_score: Optional[int] = None
    audience_score: Optional[int] = None
    critics_count: Optional[int] = None
    audience_count: Optional[int] = None
    last_updated: Optional[datetime] = None

class WikipediaData(BaseModel):
    summary: Optional[str] = None
    page_title: Optional[str] = None
    last_updated: Optional[datetime] = None

class Movie(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="IMDB ID usually, e.g., tt1375666")
    title: str
    original_title: Optional[str] = None
    
    language: Optional[str] = "en"
    regions: List[str] = Field(default_factory=list)
    
    release_date: Optional[datetime] = None
    runtime_minutes: Optional[int] = None
    
    genres: List[str] = Field(default_factory=list)
    
    certification: Optional[Certification] = None
    
    crew: Optional[Crew] = None
    
    cast: List[str] = Field(default_factory=list)
    
    imdb: Optional[IMDBData] = None
    rotten_tomatoes: Optional[RottenTomatoesData] = None
    wikipedia: Optional[WikipediaData] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class RedditComment(BaseModel):
    comment_id: str
    text: str
    score: Optional[int] = 0
    created_at: Optional[datetime] = None

class RedditPost(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    post_id: str
    subreddit: str
    title: str
    selftext: Optional[str] = None
    url: str
    
    score: Optional[int] = 0
    num_comments: Optional[int] = 0
    
    created_at: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    comments: List[RedditComment] = Field(default_factory=list)
    
    comment_limit: Optional[int] = 50
    comment_sort: Optional[str] = "top"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class YouTubeStats(BaseModel):
    views: Optional[int] = 0
    likes: Optional[int] = 0
    comment_count: Optional[int] = 0

class YouTubeComment(BaseModel):
    comment_id: str
    text: str
    likes: Optional[int] = 0
    created_at: Optional[datetime] = None

class YouTubeVideo(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    video_id: str
    video_type: str = Field(..., description="trailer | review | interview")
    
    title: str
    channel: str
    url: str
    
    published_at: Optional[datetime] = None
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    stats: Optional[YouTubeStats] = None
    
    comments: List[YouTubeComment] = Field(default_factory=list)
    
    comment_limit: Optional[int] = 100
    comment_sort: Optional[str] = "top"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class EventSource(BaseModel):
    source_type: str = Field(..., alias="type")
    url: Optional[str] = None
    confidence: Optional[str] = "medium"

class MovieEvent(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    event_type: str
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    
    source: Optional[EventSource] = None
    detected_by: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class TrendsDerived(BaseModel):
    momentum: Optional[float] = None
    volatility: Optional[float] = None

class GoogleTrends(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    region: str
    
    date: Optional[datetime] = None
    interest: int
    
    derived: Optional[TrendsDerived] = None
    
    source: str = "google_trends"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class TimeWindow(BaseModel):
    start: Optional[datetime] = Field(None, alias="from")
    end: Optional[datetime] = Field(None, alias="to")

class NarrativeSection(BaseModel):
    summary: Optional[str] = None
    tone: Optional[str] = None

class NarrativeSections(BaseModel):
    critics: Optional[NarrativeSection] = None
    general_public: Optional[NarrativeSection] = None
    actor_perception: Optional[NarrativeSection] = None

class NarrativeSource(BaseModel):
    generator: str = "grok"
    prompt_version: Optional[str] = None
    confidence: Optional[str] = "medium"

class TwitterNarrative(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    time_window: Optional[TimeWindow] = Field(None, alias="time_window")
    
    sections: Optional[NarrativeSections] = None
    
    overall_tone: Optional[str] = None
    
    source: Optional[NarrativeSource] = None
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
