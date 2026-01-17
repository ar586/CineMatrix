import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient
from backend.ingestion.pipeline import DataPipeline

def run():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    movie_title = "Tumbbad"
    movie = db.movies.find_one({"title": movie_title})
    
    if not movie:
        print(f"Movie '{movie_title}' not found. Creating placeholder.")
        res = db.movies.insert_one({"title": movie_title, "movie_id": "tt8239946", "is_active": True})
        movie_id = str(res.inserted_id)
    else:
        movie_id = str(movie["_id"])
        print(f"Found '{movie_title}' with ID: {movie_id}")
        
    print("Running Pipeline...")
    pipeline = DataPipeline()
    pipeline.run_pipeline(movie_title, movie_id)
    print("Ingestion Complete.")
    
    # Verify Reddit Posts
    count = db.reddit_posts.count_documents({"movie_id": movie_id})
    print(f"Reddit Posts in DB: {count}")
    
    # Check for comments
    sample = db.reddit_posts.find_one({"movie_id": movie_id})
    if sample:
        comments = sample.get("comments", [])
        print(f"Sample Post Comments: {len(comments)}")
        if comments:
            print(f"First Comment: {comments[0].get('text')[:50]}... (Score: {comments[0].get('score')})")

if __name__ == "__main__":
    run()
