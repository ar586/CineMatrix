import sys
import os

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import backend.config # Load env vars
from backend.database.client import MongoDBClient

def test_mongo():
    print("Testing MongoDB Connection...")
    try:
        mongo = MongoDBClient()
        if mongo.client:
            print("✅ Client initialized.")
            db = mongo.get_db()
            print(f"✅ DB Accessed: {db.name}")
            collections = db.list_collection_names()
            print(f"✅ Collections: {collections}")
        else:
            print("❌ Client initialization failed (None).")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_mongo()
