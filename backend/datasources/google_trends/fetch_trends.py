
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
        Fetch trends data for a movie title.
        Returns a dict with 'interest_over_time' and 'related_queries'.
        """
        try:
            # Add small random sleep to avoid rate limits if called rapidly (though single call is fine)
            # time.sleep(random.uniform(1, 2))
            
            # Format timeframe
            tf = format_timeframe(timeframe)
            
            # Build payload
            # We treat the title as the keyword.
            kw_list = [title]
            self.client.build_payload(kw_list, timeframe=tf)
            
            # Fetch Data
            interest_df = self.client.interest_over_time()
            related_dict = self.client.related_queries()
            
            # Parse Data
            interest_data = self.parser.parse_interest_over_time(interest_df)
            related_data = self.parser.parse_related_queries(related_dict)
            
            return {
                "keyword": title,
                "timeframe": tf,
                "interest_over_time": interest_data,
                "related_queries": related_data
            }
            
        except Exception as e:
            print(f"Error fetching trends for {title}: {e}")
            # If rate limit (429), we might want to return specific error
            return None

# Simple main for testing
if __name__ == "__main__":
    fetcher = TrendsFetcher()
    title = "Inception"
    print(f"Fetching trends for {title}...")
    data = fetcher.get_movie_trends(title)
    
    if data:
        print(f"Found {len(data['interest_over_time'])} data points for interest over time.")
        if data['related_queries']:
            print("Top related queries:")
            top = data['related_queries'].get(title, {}).get('top', [])
            for t in top[:5]:
                print(f"- {t['query']} ({t['value']})")
    else:
        print("No data found or error occurred.")
