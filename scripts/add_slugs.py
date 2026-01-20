#!/usr/bin/env python3
"""
Migration Script: Add Slugs to Existing Movies
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.client import MongoDBClient
from bson import ObjectId

def create_slug(title, year=None):
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    if year:
        return f"{slug}-{year}"
    return slug

def migrate_movies():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    movies = list(db.movies.find({"slug": {"$exists": False}}))
    print(f"Found {len(movies)} movies needing slugs.")
    
    for movie in movies:
        title = movie.get("title")
        if not title:
            continue
            
        slug = create_slug(title)
        
        # Check collision
        if db.movies.find_one({"slug": slug}):
            print(f"Collision for {slug}. Resolving...")
            counter = 1
            while db.movies.find_one({"slug": f"{slug}-{counter}"}):
                counter += 1
            slug = f"{slug}-{counter}"
            
        db.movies.update_one(
            {"_id": movie["_id"]},
            {"$set": {"slug": slug}}
        )
        print(f"Updated '{title}' -> '{slug}'")
        
    print("Migration complete.")

if __name__ == "__main__":
    migrate_movies()
