
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

class GoogleTrendsClient:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables.")

    def get_trends_data(self, query, timeframe='today 5-y', geo='US'):
        """
        Fetch trends data using SerpApi.
        :param query: Search query (e.g. movie title)
        :param timeframe: Date range (e.g. 'today 12-m', '2016-10-10 2017-10-10')
        :param geo: Geographic location (e.g. 'US')
        :return: Dict containing the JSON response
        """
        params = {
            "engine": "google_trends",
            "q": query,
            "date": timeframe,
            "geo": geo,
            "api_key": self.api_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        return results
