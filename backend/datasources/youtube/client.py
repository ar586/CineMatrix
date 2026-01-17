
from googleapiclient.discovery import build
import os

class YouTubeClient:
    def __init__(self):
        """
        Initialize YouTube Client.
        Expects 'YOUTUBE_API_KEY' in environment variables.
        """
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None

    def search_videos(self, query, max_results=5):
        """
        Search for videos by query.
        Returns the raw search response.
        """
        try:
            if not self.youtube:
                if self.serpapi_key:
                     return self._search_serpapi(query, max_results)
                raise ValueError("YOUTUBE_API_KEY not found.")

            request = self.youtube.search().list(
                part="snippet",
                q=query,
                maxResults=max_results,
                type="video"
            )
            return request.execute()
        except Exception as e:
            # Fallback to SerpApi on Quota Error
            if self.serpapi_key and ("quota" in str(e).lower() or "403" in str(e)):
                print(f"⚠️ YouTube Quota Exceeded. Falling back to SerpApi for '{query}'...")
                return self._search_serpapi(query, max_results)
            raise e

    def _search_serpapi(self, query, max_results):
        """
        Fallback search using SerpApi (engine=youtube)
        """
        from serpapi import GoogleSearch
        
        params = {
            "engine": "youtube",
            "search_query": query,
            "api_key": self.serpapi_key
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            video_results = results.get("video_results", [])
            
            # Map to YouTube Data API format
            items = []
            for video in video_results[:max_results]:
                # Extract video ID from link
                vid_id = video.get("link", "").split("v=")[-1].split("&")[0]
                
                items.append({
                    "id": {"videoId": vid_id},
                    "snippet": {
                        "title": video.get("title"),
                        "description": video.get("description", ""),
                        "channelTitle": video.get("channel", {}).get("name"),
                        "publishedAt": video.get("published_date") or "Recently" 
                    }
                })
            
            return {"items": items}
        except Exception as e:
            print(f"❌ SerpApi Fallback failed: {e}")
            return {"items": []}

    def get_video_details(self, video_ids):
        """
        Get details (statistics) for a list of video IDs.
        """
        if not self.youtube:
            raise ValueError("YOUTUBE_API_KEY not found.")

        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids)
        )
        return request.execute()

    def get_channel_details(self, channel_ids):
        """
        Get details for a list of channel IDs (snippet, statistics).
        """
        if not self.youtube:
            raise ValueError("YOUTUBE_API_KEY not found.")

        request = self.youtube.channels().list(
            part="snippet,statistics",
            id=",".join(channel_ids)
        )
        return request.execute()

    def get_video_comments(self, video_id, max_results=5):
        """
        Get top comments for a video.
        """
        if not self.youtube:
            raise ValueError("YOUTUBE_API_KEY not found.")

        try:
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                textFormat="plainText",
                order="relevance" 
            )
            return request.execute()
        except Exception:
            # Comments might be disabled or other error
            return None
