
import pandas as pd

class TrendsParser:
    def parse_interest_over_time(self, df):
        """
        Convert interest_over_time DataFrame to list of dicts.
        Structure: [{'date': 'YYYY-MM-DD', 'value': 100}, ...]
        """
        if df is None or df.empty:
            return []

        results = []
        # The dataframe index is the date. Columns are keywords.
        # We assume single keyword queries for now, or we take the first column.
        
        # Reset index to access date column easily
        df_reset = df.reset_index()
        
        for _, row in df_reset.iterrows():
            date_str = row['date'].strftime('%Y-%m-%d')
            # Extract values for all keywords
            # Filter out 'isPartial' column
            for col in df.columns:
                if col == 'isPartial':
                    continue
                results.append({
                    "date": date_str,
                    "keyword": col,
                    "value": int(row[col])
                })
        
        return results

    def parse_related_queries(self, queries_dict):
        """
        Convert related_queries dictionary to a simplified structure.
        """
        if not queries_dict:
            return {}

        parsed = {}
        for keyword, data in queries_dict.items():
            parsed[keyword] = {
                "top": [],
                "rising": []
            }
            
            if data['top'] is not None:
                parsed[keyword]['top'] = data['top'].to_dict(orient='records')
                
            if data['rising'] is not None:
                parsed[keyword]['rising'] = data['rising'].to_dict(orient='records')
                
        return parsed
