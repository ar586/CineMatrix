
from googleapiclient.discovery import build
import os

class YouTubeClient:
    def __init__(self):
        """
        Initialize YouTube Client.
        Expects 'YOUTUBE_API_KEY' in environment variables.
        """
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None

    def search_videos(self, query, max_results=5):
        """
        Search for videos by query.
        Returns the raw search response.
        """
        if not self.youtube:
            raise ValueError("YOUTUBE_API_KEY not found.")

        request = self.youtube.search().list(
            part="snippet",
            q=query,
            maxResults=max_results,
            type="video"
        )
        return request.execute()

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
