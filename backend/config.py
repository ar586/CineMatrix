import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Database
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "cluster0.aph22.mongodb.net")
MONGO_APP_NAME = os.getenv("MONGO_APP_NAME", "Cluster0")
MONGO_URI = os.getenv("MONGO_URI")

# Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "CineMatrix/1.0")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# xAI (Grok)
# xAI (Grok)
XAI_API_KEY = os.getenv("XAI_API_KEY")

# Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_MODEL = "models/gemma-3-27b-it" 
# Note: "google/gemma-3-27b-it" is a HuggingFace model ID, typically for local run or via specific API.
# If user provided a Gemini API Key (starts with AIza), they likely want to use the Gemini API models (gemini-pro, gemini-1.5-flash).
# "gemma-3-27b-it" isn't a standard model ID in the Gemini API (vertex might support it).
# I will stick to "gemini-1.5-flash" as a safe default for the API key provided, or "gemini-2.0-flash-exp" 
# User asked for "google/gemma-3-27b-it" - this is strange with an AIza key.
# I will use "gemini-1.5-pro" as a robust default for "Reasoning" tasks if the specific model ID fails,
# but I will try to respect the user's intent or map it.
# Actually, let's just set the variable, we can handle the mapping in the client.
LLM_MODEL_NAME = "models/gemma-3-27b-it"

# IMDB
IMDB_API_KEY = os.getenv("IMDB_API_KEY")

# Firecrawl
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def validate_config():
    """
    Checks if critical environment variables are set.
    Returns a list of missing variable names.
    """
    missing = []
    
    # Check Database (Either URI or User/Pass must be present)
    if not MONGO_URI and not (MONGO_USER and MONGO_PASSWORD):
         missing.append("MONGO_USER/MONGO_PASSWORD (or MONGO_URI)")

    # API Checks
    if not REDDIT_CLIENT_ID: missing.append("REDDIT_CLIENT_ID")
    if not REDDIT_CLIENT_SECRET: missing.append("REDDIT_CLIENT_SECRET")
    if not YOUTUBE_API_KEY: missing.append("YOUTUBE_API_KEY")
    # if not XAI_API_KEY: missing.append("XAI_API_KEY") # Optional for now
    if not IMDB_API_KEY: missing.append("IMDB_API_KEY")
    if not FIRECRAWL_API_KEY: missing.append("FIRECRAWL_API_KEY")
    
    return missing
