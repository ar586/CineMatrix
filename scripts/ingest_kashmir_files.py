"""
Ingest data for The Kashmir Files (2022)
IMDB ID: tt10811166
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import AgentOrchestrator
from backend.database.client import MongoDBClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Movie details
    movie_id = "tt10811166"  # The Kashmir Files IMDB ID
    movie_title = "The Kashmir Files"
    
    print(f"\n{'='*60}")
    print(f"Starting data ingestion for: {movie_title}")
    print(f"IMDB ID: {movie_id}")
    print(f"{'='*60}\n")
    
    # Initialize database
    client = MongoDBClient()
    db = client.get_db()
    
    # Check if movie already exists
    existing = db.movies.find_one({"movie_id": movie_id})
    if existing:
        print(f"✅ Movie already exists in database: {existing.get('title')}")
    else:
        print(f"⚠️  Movie not found in database, will be created during ingestion")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Run the pipeline
    print(f"\n🚀 Starting orchestrator for {movie_title}...")
    result = orchestrator.process_movie(movie_id, movie_title)
    
    print(f"\n{'='*60}")
    print(f"Ingestion Complete!")
    print(f"{'='*60}")
    
    # Show summary
    if result:
        print(f"\n📊 Summary:")
        print(f"  Movie ID: {movie_id}")
        print(f"  Title: {movie_title}")
        print(f"  Status: Success ✅")
        
        # Check what was created
        movie_doc = db.movies.find_one({"movie_id": movie_id})
        if movie_doc:
            print(f"\n📝 Movie Document:")
            print(f"  Title: {movie_doc.get('title')}")
            print(f"  Year: {movie_doc.get('year')}")
            print(f"  Genres: {', '.join(movie_doc.get('genres', []))}")
            
        # Check data counts
        reddit_count = db.reddit_posts.count_documents({"movie_id": movie_id})
        youtube_count = db.youtube_videos.count_documents({"movie_id": movie_id})
        news_count = db.news_articles.count_documents({"movie_id": movie_id})
        sentiments_count = db.source_sentiments.count_documents({"movie_id": movie_id})
        
        print(f"\n📈 Data Collected:")
        print(f"  Reddit Posts: {reddit_count}")
        print(f"  YouTube Videos: {youtube_count}")
        print(f"  News Articles: {news_count}")
        print(f"  Sentiment Records: {sentiments_count}")
    else:
        print(f"  Status: Failed ❌")

if __name__ == "__main__":
    main()
