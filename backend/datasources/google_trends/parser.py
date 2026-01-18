
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

    def parse_interest_by_region(self, trends_data):
        """
        Extract interest_by_region from SerpApi response.
        """
        results = []
        # SerpApi structure: "interest_by_region": [{"location": "New York", "value": "100", ...}]
        region_section = trends_data.get("interest_by_region", [])
        
        if not region_section:
            return []
            
        for item in region_section:
            results.append({
                "location": item.get("location"),
                "value": item.get("extracted_value")
            })
            
        # Return top 20 regions to avoid bloating data
        return sorted(results, key=lambda x: x['value'] if x['value'] is not None else 0, reverse=True)[:20]

    def parse_related_topics(self, trends_data):
        """
        Extract related_topics from SerpApi response.
        """
        parsed = {}
        # SerpApi structure similar to related_queries
        topic_section = trends_data.get("related_topics", {})
        
        for key, data in topic_section.items():
            parsed[key] = {
                "top": [],
                "rising": []
            }
            
            top_topics = data.get("top", [])
            rising_topics = data.get("rising", [])
            
            if top_topics:
                parsed[key]['top'] = [
                    {
                        "topic": t.get("topic", {}).get("title"),
                        "type": t.get("topic", {}).get("type"),
                        "value": t.get("extracted_value")
                    }
                    for t in top_topics
                ]
                
            if rising_topics:
                parsed[key]['rising'] = [
                    {
                        "topic": t.get("topic", {}).get("title"),
                        "type": t.get("topic", {}).get("type"),
                        "value": t.get("value")
                    }
                    for t in rising_topics
                ]
        
        return parsed
