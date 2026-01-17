
from .client import YouTubeClient
from .parser import YouTubeParser
from .transcript import get_video_transcript
import os

class YouTubeFetcher:
    def __init__(self):
        self.client = YouTubeClient()
        self.parser = YouTubeParser()

    def get_movie_trailers(self, title, max_results=3):
        """
        Fetch official trailers for a movie.
        """
        query = f"{title} official trailer"
        return self._fetch_videos(query, max_results)

    def get_movie_reviews(self, title, max_results=5):
        """
        Fetch movie reviews.
        """
        query = f"{title} movie review"
        return self._fetch_videos(query, max_results)

    def search_trailers_and_reviews(self, title, max_results=5):
        """
        Fetch both trailers and reviews and combine them.
        """
        trailers = self.get_movie_trailers(title, max_results=max_results)
        reviews = self.get_movie_reviews(title, max_results=max_results)
        # Deduplicate by video_id
        seen_ids = set()
        combined = []
        for v in trailers + reviews:
            if v['video_id'] not in seen_ids:
                combined.append(v)
                seen_ids.add(v['video_id'])
        return combined

    def _fetch_videos(self, query, max_results):
        try:
            if not self.client.api_key:
                print("YOUTUBE_API_KEY is missing. Skipping YouTube fetch.")
                return []

            # 1. Search to get IDs
            search_response = self.client.search_videos(query, max_results)
            video_ids = [item['id']['videoId'] for item in search_response.get('items', []) if item['id'].get('videoId')]
            
            if not video_ids:
                return []
                
            # 2. Get details for these IDs (to get views, duration)
            details_response = self.client.get_video_details(video_ids)
            
            # 3. Parse initial video details
            videos = self.parser.parse_videos(details_response.get('items', []))
            
            # 4. Enhance with Channel Info and Comments
            channel_ids = list(set([v.get("channel_id") for v in videos if v.get("channel_id")]))
            
            channel_map = {}
            if channel_ids:
                try:
                    c_resp = self.client.get_channel_details(channel_ids)
                    channel_map = self.parser.parse_channels(c_resp.get("items", []))
                except Exception as e:
                    print(f"Error fetching channels: {e}")

            for video in videos:
                # Add channel info
                c_info = channel_map.get(video.get("channel_id"))
                if c_info:
                    video["channel_image"] = c_info["image"]
                    video["channel_subs"] = c_info["subs"]

                # Fetch Transcript
                video["transcript"] = get_video_transcript(video["video_id"])
                
                # Fetch comments (Top 3)
                try:
                    c_resp = self.client.get_video_comments(video["video_id"], max_results=3)
                    if c_resp:
                        video["comments"] = self.parser.parse_comments(c_resp.get("items", []))
                except Exception as e:
                    # Comments might be disabled or quota reached
                    pass
            
            return videos
            
        except Exception as e:
            print(f"Error fetching YouTube videos for query '{query}': {e}")
            return []

if __name__ == "__main__":
    fetcher = YouTubeFetcher()
    title = "Inception"
    print(f"Fetching trailers for {title}...")
    trailers = fetcher.get_movie_trailers(title)
    
    if trailers:
        print(f"Found {len(trailers)} trailers:")
        for t in trailers:
            print(f"- {t['title']} ({t['views']} views) [{t['duration']}]")
    else:
        print("No trailers found or API key missing.")
