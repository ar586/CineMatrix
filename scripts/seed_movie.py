import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import backend.config
from backend.database.client import MongoDBClient

def seed_movie():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    # Check if Inception exists
    existing = db.movies.find_one({"movie_id": "tt1375666"})
    
    if existing:
        print("Found Inception. Updating is_active=True...")
        db.movies.update_one(
            {"movie_id": "tt1375666"},
            {"$set": {"is_active": True, "title": "Inception"}}
        )
    else:
        print("Seeding Inception...")
        db.movies.insert_one({
            "movie_id": "tt1375666",
            "title": "Inception",
            "is_active": True,
            "created_at": datetime.utcnow()
        })
    
    print("✅ Seed Complete.")

if __name__ == "__main__":
    seed_movie()
