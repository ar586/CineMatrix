import sys
import os

# Robust path addition
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.client import MongoDBClient

def clean_null_ids():
    mongo = MongoDBClient()
    db = mongo.get_db()
    
    print("Checking collection: source_sentiments")
    
    # Check for null _ids
    null_docs = list(db.source_sentiments.find({"_id": None}))
    print(f"Found {len(null_docs)} documents with _id: null")
    
    if null_docs:
        print("Deleting them...")
        db.source_sentiments.delete_many({"_id": None})
        print("Deleted.")

    # Check for anything suspicious
    count = db.source_sentiments.count_documents({})
    print(f"Total documents: {count}")

if __name__ == "__main__":
    clean_null_ids()
