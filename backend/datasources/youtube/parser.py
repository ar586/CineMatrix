
from .utils import parse_duration

class YouTubeParser:
    def parse_videos(self, items):
        """
        Parse a list of video items (from videos().list()).
        """
        results = []
        for item in items:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            
            results.append({
                "id": item.get("id"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "channel": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "views": stats.get("viewCount"),
                "likes": stats.get("likeCount"),
                "duration": parse_duration(content.get("duration")),
                "url": f"https://www.youtube.com/watch?v={item.get('id')}"
            })
        return results
