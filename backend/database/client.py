
from pymongo import MongoClient
import os

class MongoDBClient:
    def __init__(self):
        """
        Initialize MongoDB Client.
        Uses environment variable 'MONGO_URI' or falls back to provided credentials.
        """
        # Default credentials provided by user
        default_user = os.getenv("MONGO_USER")
        default_pass = os.getenv("MONGO_PASSWORD")
        default_cluster = os.getenv("MONGO_CLUSTER", "cluster0.aph22.mongodb.net")
        default_app_name = os.getenv("MONGO_APP_NAME", "Cluster0")
        
        if default_user and default_pass:
             default_uri = f"mongodb+srv://{default_user}:{default_pass}@{default_cluster}/?appName={default_app_name}"
        else:
             default_uri = None
        
        self.uri = os.getenv("MONGO_URI", default_uri)
        
        try:
            self.client = MongoClient(self.uri)
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            print(f"MongoDB Connection Error: {e}")
            self.client = None

    def get_client(self):
        return self.client

    def get_db(self, db_name="CineMatrix"):
        if self.client:
            return self.client[db_name]
        return None

if __name__ == "__main__":
    # Test connection
    mongo = MongoDBClient()
    db = mongo.get_db()
    if db is not None:
        print(f"Connected to database: {db.name}")
        # List collections to verify access
        print("Collections:", db.list_collection_names())
