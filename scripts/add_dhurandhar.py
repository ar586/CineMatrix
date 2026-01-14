import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from backend.database.client import MongoDBClient
from backend.database.models import Movie
from datetime import datetime

# Connect to MongoDB
mongo = MongoDBClient()
db = mongo.get_db()

if db is None:
    print("❌ Failed to connect to database")
    sys.exit(1)

# Add Dhurandhar
movie = Movie(
    movie_id='tt32415527',  # Dhurandhar IMDB ID
    title='Dhurandhar',
    is_active=True,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

result = db.movies.update_one(
    {'movie_id': 'tt32415527'},
    {'$set': movie.model_dump(exclude={'id'})},
    upsert=True
)

if result.upserted_id:
    print(f'✅ Dhurandhar added to database (ID: {result.upserted_id})')
else:
    print(f'✅ Dhurandhar updated in database (matched: {result.matched_count})')

# List all active movies
print("\nActive movies:")
for movie in db.movies.find({'is_active': True}):
    print(f"  - {movie['title']} ({movie['movie_id']})")
