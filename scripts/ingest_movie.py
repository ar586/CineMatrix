#!/usr/bin/env python3
"""
BULLETPROOF Movie Ingestion Script
This ensures PERFECT data fetching with proper ID handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.client import MongoDBClient
from backend.ingestion.pipeline import DataPipeline
from backend.aggregation.aggregator import SentimentAggregator
from datetime import datetime, timedelta
from bson import ObjectId

def ingest_movie(movie_title: str, imdb_id: str):
    """
    Ingest a movie with bulletproof error handling
    
    Args:
        movie_title: Movie title (e.g., "Dangal")
        imdb_id: IMDB ID (e.g., "tt5074352")
    """
    
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    print("=" * 70)
    print(f"🎬 BULLETPROOF INGESTION: {movie_title}")
    print(f"📋 IMDB ID: {imdb_id}")
    print("=" * 70)
    
    # Step 1: Create or update movie document with IMDB ID
    print("\n1️⃣  Setting up movie document...")
    existing = db.movies.find_one({"movie_id": imdb_id})
    
    if existing:
        movie_obj_id = str(existing["_id"])
        print(f"   ✅ Movie exists (ObjectId: {movie_obj_id})")
        print(f"   🔄 Will update with fresh data")
    else:
        # Create new with IMDB ID as movie_id
        result = db.movies.insert_one({
            "title": movie_title,
            "movie_id": imdb_id,  # CRITICAL: Use IMDB ID, not ObjectId
            "is_active": True,
            "created_at": datetime.utcnow()
        })
        movie_obj_id = str(result.inserted_id)
        print(f"   ✅ Created new movie (ObjectId: {movie_obj_id})")
    
    # Step 2: Run the pipeline with ObjectId (for internal use)
    # The pipeline will use this to store data, but we'll fix references after
    print("\n2️⃣  Running data ingestion pipeline...")
    print("   Fetching: TMDB, IMDB, Reddit, YouTube, News, Wikipedia, Trends")
    print("   " + "-" * 66)
    
    try:
        pipeline = DataPipeline()
        # CRITICAL: Pass ObjectId to pipeline (it expects this internally)
        pipeline.run_pipeline(movie_title, movie_obj_id)
        print("   ✅ Pipeline completed")
    except Exception as e:
        print(f"   ⚠️  Pipeline error: {e}")
        print("   Continuing with data cleanup...")
    
    # Step 3: CRITICAL FIX - Update all collections to use IMDB ID
    print("\n3️⃣  Fixing data references (ObjectId → IMDB ID)...")
    
    collections_to_fix = [
        "reddit_posts",
        "youtube_videos", 
        "news_articles",
        "source_sentiments",
        "daily_movie_sentiments",
        "visualizations",
        "insights"
    ]
    
    for coll_name in collections_to_fix:
        result = db[coll_name].update_many(
            {"movie_id": movie_obj_id},
            {"$set": {"movie_id": imdb_id}}
        )
        if result.modified_count > 0:
            print(f"   ✅ {coll_name}: {result.modified_count} records updated")
    
    # Step 4: Ensure movie document has IMDB ID
    if ObjectId.is_valid(movie_obj_id):
        db.movies.update_one(
            {"_id": ObjectId(movie_obj_id)},
            {"$set": {"movie_id": imdb_id}}
        )
        print(f"   ✅ Movie document updated with IMDB ID")
    else:
        print(f"   ℹ️  Movie ID is already in correct format (not an ObjectId)")
    
    # Step 5: Run aggregation to generate insights
    print("\n4️⃣  Generating insights...")
    try:
        aggregator = SentimentAggregator()
        
        # Try today and yesterday
        for days_ago in [0, 1]:
            date = datetime.now() - timedelta(days=days_ago)
            try:
                result = aggregator.aggregate_daily_sentiment(imdb_id, date)
                if result:
                    print(f"   ✅ Aggregated sentiment for {date.date()}")
            except Exception as e:
                print(f"   ⚠️  Aggregation error for {date.date()}: {e}")
    except Exception as e:
        print(f"   ⚠️  Insight generation error: {e}")
    
    # Step 6: Comprehensive verification
    print("\n5️⃣  Verification Report")
    print("   " + "-" * 66)
    
    movie = db.movies.find_one({"movie_id": imdb_id})
    
    if not movie:
        print("   ❌ CRITICAL: Movie not found!")
        return
    
    # Check TMDB data
    tmdb_ok = movie.get("tmdb_id") is not None
    print(f"   {'✅' if tmdb_ok else '❌'} TMDB Data: {movie.get('tmdb_id', 'Missing')}")
    if tmdb_ok:
        print(f"      Budget: ${movie.get('budget', 0):,}")
        print(f"      Revenue: ${movie.get('revenue', 0):,}")
        print(f"      Director: {movie.get('crew', {}).get('director', 'N/A')}")
        print(f"      Cast: {len(movie.get('cast', []))} actors")
    
    # Check IMDB data
    imdb_ok = movie.get("imdb_rating") is not None
    print(f"   {'✅' if imdb_ok else '❌'} IMDB Data: {movie.get('imdb_rating', 'Missing')}")
    if imdb_ok:
        print(f"      Rating: {movie.get('imdb_rating')}/10")
        print(f"      Votes: {movie.get('imdb_votes', 0):,}")
        print(f"      Awards: {movie.get('awards', 'N/A')}")
    
    # Check related data
    print(f"\n   📊 Related Data:")
    counts = {
        "News Articles": db.news_articles.count_documents({"movie_id": imdb_id}),
        "Reddit Posts": db.reddit_posts.count_documents({"movie_id": imdb_id}),
        "YouTube Videos": db.youtube_videos.count_documents({"movie_id": imdb_id}),
        "Sentiments": db.source_sentiments.count_documents({"movie_id": imdb_id}),
        "Daily Aggregations": db.daily_movie_sentiments.count_documents({"movie_id": imdb_id}),
        "Insights": db.insights.count_documents({"movie_id": imdb_id}),
        "Visualizations": db.visualizations.count_documents({"movie_id": imdb_id})
    }
    
    for name, count in counts.items():
        status = "✅" if count > 0 else "⚠️ "
        print(f"      {status} {name}: {count}")
    
    # Final status
    print("\n" + "=" * 70)
    critical_ok = tmdb_ok and imdb_ok and counts["News Articles"] > 0
    
    if critical_ok:
        print("✅ SUCCESS - Movie fully ingested and ready!")
    else:
        print("⚠️  PARTIAL SUCCESS - Some data missing (see above)")
    
    print("=" * 70)
    print(f"\n🌐 Access movie at:")
    print(f"   Frontend: http://localhost:4000/movie/{imdb_id}")
    print(f"   API: http://localhost:7000/api/movies/{imdb_id}")
    print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ingest_movie.py <movie_title> <imdb_id>")
        print("Example: python ingest_movie.py 'Dangal' 'tt5074352'")
        sys.exit(1)
    
    movie_title = sys.argv[1]
    imdb_id = sys.argv[2]
    
    if not imdb_id.startswith("tt"):
        print("❌ Error: IMDB ID must start with 'tt'")
        sys.exit(1)
    
    ingest_movie(movie_title, imdb_id)
