import sys
import os

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import backend.config # Load env vars


from backend.datasources.reddit.client import RedditClient
from backend.datasources.youtube.client import YouTubeClient
from backend.datasources.imdb.client import IMDBClient
from ml.pipelines.sentiment_engine import SentimentEngine
from backend.aggregation.aggregator import SentimentAggregator
from datetime import datetime
import asyncio

async def test_pipeline(movie_title):
    print(f"🎬 Starting Pipeline Test for: {movie_title}")
    
    # 1. Fetch Metadata (IMDB)
    print("\n[1/4] Fetching Metadata...")
    imdb = IMDBClient()
    metadata = imdb.search_movie(movie_title)
    if not metadata:
        print("❌ Metadata fetch failed.")
        return
    movie_id = metadata.get("imdbID")
    print(f"✅ Found ID: {movie_id} ({metadata.get('Title')})")
    
    # 2. Ingest Data (Mocking search for now, just verifying clients work)
    print("\n[2/4] Verifying Data Sources...")
    reddit = RedditClient().get_instance()
    print(f"✅ Reddit Client: {reddit.read_only}")
    
    youtube = YouTubeClient()
    if youtube.youtube:
        print("✅ YouTube Client: Connected")
    else:
        print("❌ YouTube Client: Failed")
        
    # 3. ML Processing (Mock run)
    print("\n[3/4] Testing ML Engine...")
    engine = SentimentEngine()
    # Mocking discussion data for test
    mock_discussions = [
        {"text": "The acting was superb but the story fell flat.", "source": "reddit", "id": "1"},
        {"text": "Visuals were stunning! Best movie of the year.", "source": "youtube", "id": "2"}
    ]
    
    results = []
    print("   Running sentiment analysis on mock data...")
    for disc in mock_discussions:
        res = engine.analyze(disc["text"])
        # Construct DB object matching SentimentAnalysis model
        full_res = {
            "movie_id": movie_id,
            "sentiment": {
                "label": res.label,
                "score": res.score,
                "confidence": res.confidence
            },
            "aspects": res.aspects,
            "source": disc["source"],
            "processed_at": datetime.utcnow()
        }
        results.append(full_res)
        print(f"   Processed: {disc['text'][:30]}... -> Score: {res.score}")
        
    # 4. Aggregation
    print("\n[4/4] Testing Aggregator...")
    # We need to insert these into DB for aggregator to pick them up
    # However, for this test, we can just check if Aggregator class instantiates and has DB connection
    agg = SentimentAggregator()
    if agg.db_client:
        print("✅ Aggregator Connected to DB")
    
        # Insert mock data to DB for real test
        db = agg.db_client.get_db()
        db.source_sentiments.insert_many(results)
        print(f"   Inserted {len(results)} mock records to DB.")
        
        # Run aggregation
        daily_sent = agg.aggregate_daily_sentiment(movie_id, datetime.utcnow())
        if daily_sent:
            print(f"✅ Aggregation Success! Overall Sentiment: {daily_sent.overall_sentiment}")
            print(f"   Details: {daily_sent}")
        else:
            print("❌ Aggregation returned None.")

if __name__ == "__main__":
    # Remove async run if not needed, but clients might be async. 
    # Based on previous file reads, they look synchronous.
    asyncio.run(test_pipeline("Inception"))
