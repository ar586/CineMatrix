
from .client import RedditClient
from .parser import RedditParser
import praw

class RedditFetcher:
    def __init__(self):
        self.client = RedditClient()
        self.parser = RedditParser()

    def get_movie_discussions(self, title, limit=10):
        """
        Search for movie discussions on Reddit.
        """
        try:
            reddit = self.client.get_instance()
            
            # Simple search. We can also restrict to specific subreddits like r/movies
            # query = f'subreddit:movies title:"{title}"'
            query = title
            
            # Search broadly (all subreddits) or specific ones
            # Let's search all for now, sorted by relevance or top
            submissions = reddit.subreddit("all").search(query, sort="relevance", limit=limit)
            
            return self.parser.parse_posts(submissions)
            
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
            if "OAuthException" in str(e) or "401" in str(e):
                print("Check your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
            return []

if __name__ == "__main__":
    fetcher = RedditFetcher()
    title = "Inception"
    print(f"Searching Reddit for {title}...")
    posts = fetcher.get_movie_discussions(title)
    
    if posts:
        print(f"Found {len(posts)} posts:")
        for p in posts[:3]:
            print(f"- [{p['score']}] {p['title']} ({p['subreddit']})")
    else:
        print("No posts found (or auth error).")
