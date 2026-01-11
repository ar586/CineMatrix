
from typing import List, Dict
from datetime import datetime, timedelta
from agents.signals.schema import Signal
from backend.database.client import MongoDBClient
from backend.database.models import MovieEvent

class EventCorrelation:
    def __init__(self):
        self.db_client = MongoDBClient()

    def correlate(self, signals: List[Signal], movie_id: str) -> List[Signal]:
        """
        Enriches signals with potential event causes.
        """
        if not signals:
            return []

        # Fetch events for the movie
        db = self.db_client.get_db()
        # Find events around the signal dates
        # For simplicity, fetch all events for movie and filter in memory
        cursor = db.movie_events.find({"movie_id": movie_id})
        events = list(cursor) # List of dicts
        
        enriched_signals = []
        for signal in signals:
            signal_date = datetime.strptime(signal.date, "%Y-%m-%d")
            
            # Look for events in [date - 2 days, date + 1 day] window
            # Events often precede the signal
            window_start = signal_date - timedelta(days=2)
            window_end = signal_date + timedelta(days=1)
            
            related_events = []
            for event in events:
                # event['date'] might be string or datetime, assuming stored as datetime or ISO string
                # DB schema says 'date: datetime'
                evt_date = event.get("date")
                if isinstance(evt_date, str):
                    try:
                        evt_date = datetime.fromisoformat(evt_date.replace("Z", "+00:00"))
                    except:
                        continue
                
                if not evt_date:
                    continue
                    
                # Naive date comparison (ignoring time if needed)
                if window_start.date() <= evt_date.date() <= window_end.date():
                    related_events.append({
                        "event_id": str(event.get("_id", "")),
                        "type": event.get("event_type"),
                        "description": event.get("description")
                    })
            
            if related_events:
                # Add context to signal metadata
                # Note: Signal model allows dynamic metadata? Yes Dict[str, Any]
                signal.metadata["related_events"] = related_events
                
            enriched_signals.append(signal)
            
        return enriched_signals
