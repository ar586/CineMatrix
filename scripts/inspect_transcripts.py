import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient

def verify():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    movie_id_imdb = "tt1343727"
    
    print("\n--- YouTube Transcript Verification ---")
    videos = list(db.youtube_videos.find({"movie_id": movie_id_imdb}))
    print(f"Total Videos: {len(videos)}")
    
    for v in videos:
        t_len = len(v.get("transcript", "") or "")
        print(f"Video {v['video_id']}: Transcript Length = {t_len}")
        if t_len > 0:
            print(f"   Sample: {v['transcript'][:50]}...")

if __name__ == "__main__":
    verify()
