
from .client import WikipediaClient
from .utils import clean_text

class EventFetcher:
    def __init__(self):
        self.client = WikipediaClient()

    def get_events(self, title):
        """
        Fetch events or controversies related to a topic/movie.
        """
        page = self.client.get_page(title)
        if not page.exists():
            return []
            
        # Example logic: extract sections named "Controversy" or "Production"
        events = []
        target_sections = ["Controversy", "Production", "Release"]
        
        for section in page.sections:
            if any(t in section.title for t in target_sections):
                events.append({
                    "type": section.title,
                    "content": clean_text(section.text[:500]) + "..." # truncated
                })
                
        return events
