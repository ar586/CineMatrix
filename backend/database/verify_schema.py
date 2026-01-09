
from backend.database.models import Movie
from datetime import datetime

# Example data from user (adapted for Python types)
movie_data = {
  "movie_id": "tt1375666",
  "title": "Inception",
  "original_title": "Inception",
  "language": "en",
  "regions": ["US", "IN"],
  "release_date": datetime(2010, 7, 16),
  "runtime_minutes": 148,
  "genres": ["Sci-Fi", "Thriller"],
  "certification": {
    "US": "PG-13",
    "IN": "UA"
  },
  "crew": {
    "director": "Christopher Nolan",
    "writers": ["Christopher Nolan"],
    "producers": ["Emma Thomas"]
  },
  "cast": [
    "Leonardo DiCaprio",
    "Joseph Gordon-Levitt",
    "Elliot Page"
  ],
  "imdb": {
    "rating": 8.8,
    "votes": 2400000,
    "last_updated": datetime.now()
  },
  "rotten_tomatoes": {
    "critics_score": 87,
    "audience_score": 91,
    "critics_count": 340,
    "audience_count": 1000000,
    "last_updated": datetime.now()
  },
  "wikipedia": {
    "summary": "Inception is a 2010 science fiction film...",
    "page_title": "Inception",
    "last_updated": datetime.now()
  }
}

try:
    # Attempt to validate
    movie = Movie(**movie_data)
    print("Successfully validated Movie model!")
    print(f"Title: {movie.title}")
    print(f"Director: {movie.crew.director}")
    print(f"IMDB Rating: {movie.imdb.rating}")
    print(f"JSON Dump: {movie.model_dump_json(exclude_none=True)}")
except Exception as e:
    print(f"Movie Validation Error: {e}")

from backend.database.models import RedditPost

reddit_data = {
  "movie_id": "tt1375666",
  "post_id": "abc123",
  "subreddit": "movies",
  "title": "Inception ending discussion",
  "selftext": "I just watched Inception and the ending confused me...",
  "url": "https://www.reddit.com/r/movies/comments/abc123",
  "score": 1240,
  "num_comments": 542,
  "created_at": datetime(2010, 7, 17, 12, 30, 0),
  "comments": [
    {
      "comment_id": "c1",
      "text": "The ending is intentionally ambiguous.",
      "score": 421,
      "created_at": datetime.now()
    },
    {
      "comment_id": "c2",
      "text": "Nolan confirmed it was a dream.",
      "score": 212,
      "created_at": datetime.now()
    }
  ],
  "comment_limit": 50,
  "comment_sort": "top"
}

try:
    print("\n--- Verifying Reddit Post Model ---")
    post = RedditPost(**reddit_data)
    print("Successfully validated RedditPost model!")
    print(f"Post Title: {post.title}")
    print(f"Comments count: {len(post.comments)}")
    print(f"First comment: {post.comments[0].text}")
except Exception as e:
    print(f"Reddit Validation Error: {e}")

from backend.database.models import YouTubeVideo

youtube_data = {
  "movie_id": "tt1375666",
  "video_id": "XQZ123ABC",
  "video_type": "trailer",
  "title": "Inception Official Trailer",
  "channel": "Warner Bros. Pictures",
  "url": "https://www.youtube.com/watch?v=XQZ123ABC",
  "published_at": datetime(2010, 5, 10),
  "stats": {
    "views": 128000000,
    "likes": 2400000,
    "comment_count": 380000
  },
  "comments": [
    {
      "comment_id": "ytc1",
      "text": "This movie changed cinema forever.",
      "likes": 5600,
      "created_at": datetime.now()
    },
    {
      "comment_id": "ytc2",
      "text": "Hans Zimmer carried this film.",
      "likes": 4300,
      "created_at": datetime.now()
    }
  ],
  "comment_limit": 100,
  "comment_sort": "top"
}

try:
    print("\n--- Verifying YouTube Video Model ---")
    video = YouTubeVideo(**youtube_data)
    print("Successfully validated YouTubeVideo model!")
    print(f"Video Title: {video.title}")
    print(f"Views: {video.stats.views}")
    print(f"First comment: {video.comments[0].text}")
except Exception as e:
    print(f"YouTube Validation Error: {e}")

from backend.database.models import MovieEvent

event_data = {
  "movie_id": "tt1375666",
  "event_type": "controversy",
  "title": "Backlash over ambiguous ending",
  "description": "Audiences expressed confusion over the climax.",
  "event_date": datetime(2010, 7, 18),
  "source": {
    "type": "wikipedia",
    "url": "https://en.wikipedia.org/wiki/Inception",
    "confidence": "high"
  },
  "detected_by": "wikipedia_parser"
}

try:
    print("\n--- Verifying Movie Event Model ---")
    event = MovieEvent(**event_data)
    print("Successfully validated MovieEvent model!")
    print(f"Event Title: {event.title}")
    print(f"Source Type: {event.source.source_type}")
    print(f"Confidence: {event.source.confidence}")
except Exception as e:
    print(f"Event Validation Error: {e}")

from backend.database.models import GoogleTrends

trends_data = {
  "movie_id": "tt1375666",
  "region": "IN",
  "date": datetime(2026, 1, 7),
  "interest": 78,
  "derived": {
    "momentum": 0.42,
    "volatility": 0.18
  },
  "source": "google_trends"
}

try:
    print("\n--- Verifying Google Trends Model ---")
    trend = GoogleTrends(**trends_data)
    print("Successfully validated GoogleTrends model!")
    print(f"Interest: {trend.interest}")
    print(f"Derived Momentum: {trend.derived.momentum}")
    print(f"Region: {trend.region}")
except Exception as e:
    print(f"Google Trends Validation Error: {e}")

from backend.database.models import TwitterNarrative

narrative_data = {
  "movie_id": "tt1375666",
  "time_window": {
    "from": datetime(2026, 1, 1),
    "to": datetime(2026, 1, 7)
  },
  "sections": {
    "critics": {
      "summary": "Critics are divided...",
      "tone": "mixed"
    },
    "general_public": {
      "summary": "Memes and sarcasm dominate...",
      "tone": "negative"
    },
    "actor_perception": {
      "summary": "Lead actor praised...",
      "tone": "positive"
    }
  },
  "overall_tone": "mixed-negative",
  "source": {
    "generator": "grok",
    "prompt_version": "twitter-v1",
    "confidence": "medium"
  },
  "generated_at": datetime.now()
}

try:
    print("\n--- Verifying Twitter Narrative Model ---")
    narrative = TwitterNarrative(**narrative_data)
    print("Successfully validated TwitterNarrative model!")
    print(f"Overall Tone: {narrative.overall_tone}")
    print(f"Critics Summary: {narrative.sections.critics.summary}")
    print(f"Source Generator: {narrative.source.generator}")
except Exception as e:
    print(f"Twitter Narrative Validation Error: {e}")

from backend.database.models import Insight

insight_data = {
  "movie_id": "tt1375666",
  "insight_type": "sentiment_divergence",
  "severity": "high",
  "title": "High interest despite negative sentiment",
  "summary": "Search interest remains elevated even as...",
  "evidence": {
    "sentiment_change": -0.34,
    "interest_change": 0.41,
    "time_window": "48h",
    "related_events": [
      { "event_type": "controversy", "event_date": "2026-01-06" }
    ]
  },
  "recommended_visual": {
    "component": "DualLineChart",
    "x": "date",
    "y": ["sentiment", "interest"]
  },
  "confidence": 0.88,
  "generated_by": {
    "agent": "insight_orchestrator",
    "version": "v1.0"
  },
  "generated_at": datetime.now()
}

try:
    print("\n--- Verifying Insight Model ---")
    insight = Insight(**insight_data)
    print("Successfully validated Insight model!")
    print(f"Insight Title: {insight.title}")
    print(f"Severity: {insight.severity}")
    print(f"Visual Component: {insight.recommended_visual.component}")
except Exception as e:
    print(f"Insight Validation Error: {e}")
