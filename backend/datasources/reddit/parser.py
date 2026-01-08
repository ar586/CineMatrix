
from datetime import datetime

class RedditParser:
    def parse_posts(self, submissions):
        """
        Parse a list of PRAW Submission objects into a simplified dictionary format.
        """
        results = []
        for sub in submissions:
            results.append({
                "title": sub.title,
                "score": sub.score,
                "url": sub.url,
                "num_comments": sub.num_comments,
                "created_utc": sub.created_utc,
                "created_date": datetime.utcfromtimestamp(sub.created_utc).strftime('%Y-%m-%d'),
                "permalink": f"https://www.reddit.com{sub.permalink}",
                "subreddit": sub.subreddit.display_name
            })
        return results

    def parse_comments(self, submission, limit=5):
        """
        Parse top comments from a submission.
        """
        comments = []
        submission.comments.replace_more(limit=0) # Flatten tree, resolve MoreComments
        for comment in submission.comments.list()[:limit]:
            comments.append({
                "body": comment.body,
                "score": comment.score,
                "author": str(comment.author) if comment.author else "[deleted]"
            })
        return comments
