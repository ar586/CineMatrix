
import pandas as pd
from datetime import datetime

class TrendsParser:
    def parse_interest_over_time(self, trends_data):
        """
        Extract interest_over_time from SerpApi response.
        """
        results = []
        
        # SerpApi structure: "interest_over_time": {"timeline_data": [...]}
        interest_section = trends_data.get("interest_over_time", {})
        timeline_data = interest_section.get("timeline_data", [])
        
        if not timeline_data:
            return []

        for item in timeline_data:
            # item example: {'date': 'Nov 1, 2024', 'timestamp': '1730419200', 'values': [{'query': 'Inception', 'value': '75', 'extracted_value': 75}]}
            
            # SerpApi date format might vary, but they often provide a 'date' string or timestamp.
            # Let's try to use the timestamp if available for accuracy, or parse the date string.
            
            date_str = item.get("date")
            timestamp = item.get("timestamp")
            
            # Format date as YYYY-MM-DD
            if timestamp:
                dt = datetime.fromtimestamp(int(timestamp))
                formatted_date = dt.strftime('%Y-%m-%d')
            else:
                # Fallback parsing if needed, but timestamp is usually there
                formatted_date = date_str 
            
            values = item.get("values", [])
            for val in values:
                results.append({
                    "date": formatted_date,
                    "keyword": val.get("query"),
                    "value": val.get("extracted_value")
                })
                
        return results

    def parse_related_queries(self, trends_data):
        """
        Extract related_queries from SerpApi response.
        """
        parsed = {}
        
        # SerpApi structure: "related_queries": {"query_key": {"top": [...], "rising": [...]}}
        # But wait, SerpApi usually keys by the query directly or provides a list.
        # Let's check typical response.
        # It's often "related_queries": { "query_1": { "top": [...], "rising": [...] } }
        
        related_section = trends_data.get("related_queries", {})
        
        for key, data in related_section.items():
            parsed[key] = {
                "top": [],
                "rising": []
            }
            
            top_queries = data.get("top", [])
            rising_queries = data.get("rising", [])
            
            if top_queries:
                # Transform to list of dicts: {'query': 'foo', 'value': '100'}
                # SerpApi 'top' items: {'query': 'inception cast', 'value': '100', 'extracted_value': 100}
                parsed[key]['top'] = [
                    {"query": q.get("query"), "value": q.get("extracted_value")}
                    for q in top_queries
                ]
                
            if rising_queries:
                # SerpApi 'rising' items: {'query': '...', 'value': 'Breakout'}
                parsed[key]['rising'] = [
                    {"query": q.get("query"), "value": q.get("value")}
                    for q in rising_queries
                ]
                
        return parsed
