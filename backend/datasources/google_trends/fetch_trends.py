
from .client import GoogleTrendsClient
from .parser import TrendsParser
from .utils import format_timeframe
import time
import random

class TrendsFetcher:
    def __init__(self):
        self.client = GoogleTrendsClient()
        self.parser = TrendsParser()

    def get_movie_trends(self, title, timeframe='today 5-y'):
        """
        Fetch trends data for a movie title using SerpApi.
        Returns a dict with 'interest_over_time' and 'related_queries'.
        """
        try:
            # Format timeframe
            tf = format_timeframe(timeframe)
            
            # Fetch Data via SerpApi
            # SerpApi expects date format like "today 12-m" or "2024-01-01 2024-12-31"
            # Our utils.format_timeframe handles this conversion usually.
            
            raw_data = self.client.get_trends_data(query=title, timeframe=tf)
            
            if "error" in raw_data:
                print(f"SerpApi Error: {raw_data['error']}")
                return None
            
            # Parse Data
            interest_data = self.parser.parse_interest_over_time(raw_data)
            related_data = self.parser.parse_related_queries(raw_data)
            region_data = self.parser.parse_interest_by_region(raw_data)
            topic_data = self.parser.parse_related_topics(raw_data)
            
            return {
                "keyword": title,
                "timeframe": tf,
                "interest_over_time": interest_data,
                "interest_by_region": region_data,
                "related_queries": related_data,
                "related_topics": topic_data
            }
            
        except Exception as e:
            print(f"Error fetching trends for {title}: {e}")
            return None


