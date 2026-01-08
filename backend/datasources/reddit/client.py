
import praw
import os
import sys

class RedditClient:
    def __init__(self):
        """
        Initialize the Reddit client using credentials from environment variables.
        """
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "CineMatrix/1.0"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD")
        )
        
        # We can implement a check here, or let it fail when used if auth is bad.
        # But 'read_only' mode works without username/password if only client_id/secret are present.
        self.reddit.read_only = True

    def get_instance(self):
        return self.reddit
