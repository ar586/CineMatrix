
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List, Annotated, Union, Dict
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
    movie_id: Optional[str] = Field(None, description="IMDB ID usually, e.g., tt1375666")
    tmdb_id: Optional[int] = None
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
    
    metascore: Optional[int] = None
    box_office: Optional[str] = None
    awards: Optional[str] = None
    
    # TMDB-specific fields
    budget: Optional[int] = None
    revenue: Optional[int] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    tagline: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    production_companies: List[str] = Field(default_factory=list)
    trailers: List[Dict] = Field(default_factory=list)
    collection: Optional[Dict] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    is_active: bool = Field(default=True, description="Whether the movie is active for daily processing")
    
    def model_post_init(self, __context):
        # Sync movie_id with _id if movie_id is not set
        if not self.movie_id and self.id:
            self.movie_id = str(self.id)

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

class RelatedEvent(BaseModel):
    event_type: str
    event_date: Optional[str] = None # Keeping as string as per example "2026-01-06", or could parse to date

class Evidence(BaseModel):
    sentiment_change: Optional[float] = None
    interest_change: Optional[float] = None
    time_window: Optional[str] = None
    related_events: List[RelatedEvent] = Field(default_factory=list)

class RecommendedVisual(BaseModel):
    component: str
    x: str
    y: List[str] = Field(default_factory=list)

class GeneratorInfo(BaseModel):
    agent: str
    version: str

class Insight(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    insight_type: str
    severity: str = "medium"
    
    title: str
    summary: str
    
    evidence: Optional[Evidence] = None
    
    recommended_visual: Optional[RecommendedVisual] = None
    
    confidence: float
    
    generated_by: Optional[GeneratorInfo] = None
    
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class SourceRef(BaseModel):
    post_id: Optional[str] = None
    video_id: Optional[str] = None

class SentimentScore(BaseModel):
    label: str # positive | neutral | negative
    score: float # range [-1, +1]
    confidence: float

class Aspects(BaseModel):
    acting: Optional[float] = None
    story: Optional[float] = None
    ending: Optional[float] = None
    music: Optional[float] = None
    # Allow extra fields for dynamic aspects
    model_config = {"extra": "allow"}

class EngagementWeight(BaseModel):
    upvotes: Optional[int] = None
    comment_count: Optional[int] = None
    likes: Optional[int] = None
    views: Optional[int] = None

class ModelInfo(BaseModel):
    name: str
    version: str
    aggregation: str

class SentimentAnalysis(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    source: str # reddit | youtube
    source_ref: Optional[SourceRef] = None
    
    sentiment: SentimentScore
    aspects: Optional[Aspects] = None
    
    engagement_weight: Optional[EngagementWeight] = None
    
    model: Optional[ModelInfo] = None
    
    time_window: Optional[TimeWindow] = None
    
    processed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

class SourceBreakdown(BaseModel):
    reddit: Optional[float] = None
    youtube: Optional[float] = None
    # Allow extra fields for new sources
    model_config = {"extra": "allow"}

class Volume(BaseModel):
    reddit_posts: Optional[int] = 0
    youtube_videos: Optional[int] = 0
    # Allow extra fields
    model_config = {"extra": "allow"}

class DailyMovieSentiment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    movie_id: str = Field(..., description="Link to Movie collection")
    
    date: Union[str, datetime] = Field(..., description="Date of sentiment")
    
    overall_sentiment: float
    confidence: Optional[float] = 0.9
    
    source_breakdown: Optional[SourceBreakdown] = None
    
    aspect_summary: Optional[Aspects] = None # Reusing Aspects model from SentimentAnalysis
    
    volume: Optional[Union[int, Volume]] = None
    
    volatility: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
