
from typing import Generator
from backend.database.client import MongoDBClient

# Global client instance
_mongo_client: MongoDBClient = None

def get_mongo_client() -> MongoDBClient:
    """Get the global MongoDB client instance."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoDBClient()
    return _mongo_client

def get_db():
    """Dependency to get a database session."""
    client = get_mongo_client()
    db = client.get_db()
    try:
        yield db
    finally:
        # We don't close the connection here because we want to reuse it
        pass
