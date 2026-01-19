"""
Script to create missing movies with TMDB data
"""
import sys
import os
sys.path.append('.')

from backend.database.client import MongoDBClient
from backend.datasources.tmdb.client import TMDBClient
from backend.datasources.tmdb.parser import TMDBParser
from datetime import datetime

def create_movie_from_tmdb(movie_title: str, year: int = None):
    """Create a new movie entry with TMDB data"""
    
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    # Check if movie already exists
    existing = db.movies.find_one({"title": movie_title})
    if existing:
        print(f"ℹ️  Movie '{movie_title}' already exists, skipping...")
        return
    
    print(f"\n📽️  Creating: {movie_title}")
    
    # Initialize TMDB client
    tmdb = TMDBClient()
    parser = TMDBParser()
    
    # Search for the movie
    search_query = f"{movie_title} {year}" if year else movie_title
    search_results = tmdb.search_movie(search_query)
    
    if not search_results or 'results' not in search_results or len(search_results['results']) == 0:
        print(f"   ❌ No TMDB results found for '{movie_title}'")
        return
    
    # Get the first result (most relevant)
    tmdb_id = search_results['results'][0]['id']
    print(f"   Found TMDB ID: {tmdb_id}")
    
    # Fetch detailed movie data
    movie_details = tmdb.get_movie_details(tmdb_id)
    credits = tmdb.get_movie_credits(tmdb_id)
    
    # Parse the data
    parsed_data = parser.parse_movie_details(movie_details, credits)
    
    # Get IMDB ID from TMDB
    imdb_id = movie_details.get('imdb_id', f'tt{tmdb_id}')
    
    # Create movie document
    movie_doc = {
        'title': movie_title,
        'movie_id': imdb_id,
        'tmdb_id': parsed_data.get('tmdb_id'),
        'overview': parsed_data.get('overview'),
        'poster_url': parsed_data.get('poster_url'),
        'backdrop_url': parsed_data.get('backdrop_url'),
        'genres': parsed_data.get('genres', []),
        'cast': parsed_data.get('cast', []),
        'crew': parsed_data.get('crew', {}),
        'popularity': parsed_data.get('popularity'),
        'vote_average': parsed_data.get('vote_average'),
        'vote_count': parsed_data.get('vote_count'),
        'runtime_minutes': parsed_data.get('runtime_minutes'),
        'production_companies': parsed_data.get('production_companies', []),
        'tagline': parsed_data.get('tagline'),
        'release_date': parsed_data.get('release_date'),
        'is_active': True,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Insert the movie
    result = db.movies.insert_one(movie_doc)
    
    if result.inserted_id:
        print(f"   ✅ Successfully created {movie_title}")
        print(f"      - TMDB ID: {movie_doc.get('tmdb_id')}")
        print(f"      - IMDB ID: {movie_doc.get('movie_id')}")
        print(f"      - Cast: {len(movie_doc.get('cast', []))} members")
        print(f"      - Genres: {', '.join(movie_doc.get('genres', []))}")
        print(f"      - Rating: {movie_doc.get('vote_average', 'N/A')}/10")
        print(f"      - Poster: {'✓' if movie_doc.get('poster_url') else '✗'}")
    else:
        print(f"   ❌ Failed to create {movie_title}")

if __name__ == "__main__":
    movies_to_create = [
        ("Padmaavat", 2018),
        ("Raazi", 2018),
        ("Tumbbad", 2018)
    ]
    
    print("🎬 Creating movies with TMDB data...")
    print("=" * 50)
    
    for movie_title, year in movies_to_create:
        try:
            create_movie_from_tmdb(movie_title, year)
        except Exception as e:
            print(f"   ❌ Error creating {movie_title}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Creation complete!")
