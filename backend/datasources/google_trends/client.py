
from pytrends.request import TrendReq

class GoogleTrendsClient:
    def __init__(self, hl='en-US', tz=360):
        """
        Initialize the Google Trends client.
        :param hl: Host Language (e.g., 'en-US')
        :param tz: Timezone Offset (e.g., 360 for CST)
        """
        self.pytrends = TrendReq(hl=hl, tz=tz)

    def build_payload(self, kw_list, timeframe='today 5-y', geo=''):
        """
        Build the payload for the request.
        :param kw_list: List of keywords to search for.
        :param timeframe: Date range (e.g., 'today 5-y', 'now 1-H').
        :param geo: Geographic location (e.g., 'US', 'IN').
        """
        self.pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo, gprop='')

    def interest_over_time(self):
        """
        Get interest over time.
        Returns a pandas DataFrame.
        """
        return self.pytrends.interest_over_time()

    def related_queries(self):
        """
        Get related queries.
        Returns a dictionary of DataFrames.
        """
        return self.pytrends.related_queries()
