from datetime import datetime

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
            "sections": self._extract_sections(page),
            "last_updated": datetime.utcnow()
        }
        return data

    def _extract_sections(self, page):
        """
        Extract interesting sections from the page.
        """
        interesting_sections = ["Plot", "Synopsis", "Cast", "Production", "Reception", "Critical response", "Box office", "Accolades", "Awards"]
        
        extracted = []
        
        for section in page.sections:
            # Check if section title matches any keyword
            if any(key in section.title for key in interesting_sections):
                content = clean_text(section.text)
                if content:
                    extracted.append({
                        "title": section.title,
                        "content": content,
                        "level": 1
                    })
                
                # Also check level 2 subsections for specific details if needed (e.g. Critical reception under Reception)
                for subst in section.sections:
                     sub_content = clean_text(subst.text)
                     if sub_content:
                        extracted.append({
                            "title": f"{section.title} - {subst.title}",
                            "content": sub_content,
                            "level": 2
                        })

        return extracted
