
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
                "video_id": item.get("id"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "channel": snippet.get("channelTitle"),
                "channel_id": snippet.get("channelId"),
                "published_at": snippet.get("publishedAt"),
                "views": stats.get("viewCount"),
                "likes": stats.get("likeCount"),
                "comment_count": stats.get("commentCount"),
                "duration": parse_duration(content.get("duration")),
                "url": f"https://www.youtube.com/watch?v={item.get('id')}"
            })
        return results

    def parse_channels(self, items):
        """
        Parse channel items into a map {id: {image, subs}}.
        """
        channel_map = {}
        for item in items:
            c_id = item.get("id")
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            channel_map[c_id] = {
                "image": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                "subs": stats.get("subscriberCount")
            }
        return channel_map

    def parse_comments(self, items):
        """
        Parse comment threads into a list of simplified comments.
        """
        comments = []
        for item in items:
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            comments.append({
                "comment_id": item.get("id"),
                "text": top.get("textOriginal") or top.get("textDisplay"),
                "likes": top.get("likeCount"),
                "created_at": top.get("publishedAt")
            })
        return comments
