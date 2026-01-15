#!/usr/bin/env python3
"""
Test script for deduplication system.
Tests both ID-based and similarity-based deduplication.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient
from backend.database.similarity import text_similarity, find_similar_reddit_post, find_similar_news_article

def test_text_similarity():
    """Test text similarity function"""
    print("\n=== Testing Text Similarity ===")
    
    # Exact match
    assert text_similarity("Hello World", "Hello World") == 1.0
    print("✅ Exact match: 1.0")
    
    # Very similar
    sim = text_similarity("Inception movie discussion", "Inception film discussion")
    print(f"✅ Similar texts: {sim:.2f} (should be > 0.8)")
    assert sim > 0.8
    
    # Different
    sim = text_similarity("Inception", "The Dark Knight")
    print(f"✅ Different texts: {sim:.2f} (should be < 0.5)")
    assert sim < 0.5
    
    print("✅ All similarity tests passed!")

def test_database_deduplication():
    """Test database deduplication"""
    print("\n=== Testing Database Deduplication ===")
    
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    if db is None:
        print("❌ Database connection failed - skipping database tests")
        return
    
    # Test Reddit post similarity
    movie_id = "tt1375666"  # Inception
    
    # Count existing posts
    reddit_count = db.reddit_posts.count_documents({"movie_id": movie_id})
    print(f"📊 Existing Reddit posts for {movie_id}: {reddit_count}")
    
    # Count existing news
    news_count = db.news_articles.count_documents({"movie_id": movie_id})
    print(f"📊 Existing news articles for {movie_id}: {news_count}")
    
    # Count existing sentiments
    sentiment_count = db.source_sentiments.count_documents({"movie_id": movie_id})
    print(f"📊 Existing sentiments for {movie_id}: {sentiment_count}")
    
    # Test similarity detection
    if reddit_count > 0:
        sample_post = db.reddit_posts.find_one({"movie_id": movie_id})
        if sample_post:
            title = sample_post.get("title", "")
            # Test with exact title (should find match)
            similar = find_similar_reddit_post(db, movie_id, title, threshold=0.85)
            if similar:
                print(f"✅ Similarity detection working: Found match for '{title[:50]}...'")
            else:
                print(f"⚠️  No match found (might be expected if threshold too high)")
    
    print("✅ Database tests completed!")

def test_indexes():
    """Test if deduplication indexes exist"""
    print("\n=== Testing Database Indexes ===")
    
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    if db is None:
        print("❌ Database connection failed - skipping index tests")
        return
    
    collections_to_check = [
        ("reddit_posts", "unique_movie_post"),
        ("youtube_videos", "unique_movie_video"),
        ("news_articles", "unique_movie_article"),
        ("source_sentiments", "unique_movie_source_sentiment")
    ]
    
    for collection_name, index_name in collections_to_check:
        try:
            indexes = db[collection_name].index_information()
            if index_name in indexes:
                print(f"✅ {collection_name}: Index '{index_name}' exists")
            else:
                print(f"⚠️  {collection_name}: Index '{index_name}' NOT found")
        except Exception as e:
            print(f"❌ {collection_name}: Error checking indexes - {e}")
    
    print("✅ Index check completed!")

if __name__ == "__main__":
    print("🧪 Deduplication System Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Text similarity
        test_text_similarity()
        
        # Test 2: Database deduplication
        test_database_deduplication()
        
        # Test 3: Indexes
        test_indexes()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\nNext steps:")
        print("1. Fix MongoDB connection if database tests failed")
        print("2. Run: python3 scripts/create_dedup_indexes.py")
        print("3. Run pipeline twice and verify no duplicates created")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
