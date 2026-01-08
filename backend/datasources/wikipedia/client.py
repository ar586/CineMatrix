import wikipediaapi

class WikipediaClient:
    def __init__(self, language='en', user_agent="CineMatrix-Scraper/1.0 (contact@cinematrix.com)"):
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=user_agent,
            language=language
        )

    def get_page(self, title):
        """
        Fetch a single page by title.
        Returns a WikipediaPage object.
        """
        page = self.wiki.page(title)
        if not page.exists():
            return None
        return page
