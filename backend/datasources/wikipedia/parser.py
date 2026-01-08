
from .utils import clean_text

class WikipediaParser:
    def extract_movie_details(self, page):
        """
        Extracts structured data from a WikipediaPage object.
        """
        data = {
            "title": page.title,
            "url": page.fullurl,
            "summary": clean_text(page.summary),
            "plot": self._extract_plot(page),
            # Infobox extraction via wikipedia-api is limited to text.
            # We might simply capture the summary + plot for now, 
            # or if we really need key-value pairs, we'd need to parse page.html().
            # For this step, I will focus on the text content available via API.
        }
        return data

    def _extract_plot(self, page):
        """
        Finds the 'Plot' or 'Synopsis' section in the page sections.
        """
        # Recursively find sections
        def find_section(sections, keywords):
            for s in sections:
                if any(k in s.title for k in keywords):
                    return s.text
                # Check subsections
                found = find_section(s.sections, keywords)
                if found:
                    return found
            return None

        keywords = ["Plot", "Synopsis", "Plot summary"]
        plot_text = find_section(page.sections, keywords)
        
        return clean_text(plot_text) if plot_text else "Plot not found."
