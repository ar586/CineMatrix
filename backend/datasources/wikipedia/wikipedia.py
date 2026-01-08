
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

class WikipediaMovieScraper:
    BASE_URL = "https://en.wikipedia.org"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def search_movie(self, title):
        """
        Search for a movie on Wikipedia and return the URL of the first result.
        Uses the OpenSearch API for better accuracy.
        """
        search_url = f"{self.BASE_URL}/w/api.php"
        params = {
            "action": "opensearch",
            "search": title,
            "limit": 5,
            "namespace": 0,
            "format": "json"
        }
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # data format: [query, [titles], [descriptions], [urls]]
            if data and len(data) > 3 and data[3]:
                # Prefer matches with 'film' in the title or description if multiple results
                # But for now, just take the first one or logic to find "film"
                titles = data[1]
                urls = data[3]
                
                for i, t in enumerate(titles):
                    if "film" in t.lower() or "movie" in t.lower():
                        return urls[i]
                
                # Fallback to the first result if no "film" keyword found
                return urls[0]
            
            return None
        except Exception as e:
            print(f"Error searching for movie: {e}")
            return None

    def scrape_details(self, url):
        """
        Scrape movie details from the given Wikipedia URL.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = {
                "title": self._extract_title(soup),
                "url": url,
                "plot": self._extract_plot(soup),
                "infobox": self._extract_infobox(soup)
            }
            
            return data
        except Exception as e:
            print(f"Error scraping details: {e}")
            return None

    def _extract_title(self, soup):
        title_tag = soup.find("h1", {"id": "firstHeading"})
        return title_tag.get_text(strip=True) if title_tag else "Unknown Title"

    def _extract_infobox(self, soup):
        infobox_data = {}
        infobox = soup.find("table", {"class": "infobox"})
        
        if not infobox:
            return infobox_data

        rows = infobox.find_all("tr")
        for row in rows:
            header = row.find("th")
            value = row.find("td")
            
            if header and value:
                key = header.get_text(strip=True)
                # Handle lists in values (separated by br or li)
                # Replace <br> with newlines for cleaner text, or list items
                for br in value.find_all("br"):
                    br.replace_with("\n")
                for li in value.find_all("li"):
                    li.append("\n") # Ensure separation for lists
                    
                val = value.get_text(separator=" ", strip=True) 
                
                # Clean up multiple spaces/newlines
                val = re.sub(r'\s+', ' ', val).strip()
                
                infobox_data[key] = val
                
        return infobox_data

    def _extract_plot(self, soup):
        # Strategy 1: Look for id="Plot" or similar in spans (common in older/some renderings)
        plot_id = soup.find(id=re.compile(r"(Plot|Synopsis)", re.I))
        heading_tag = None
        
        if plot_id:
            # If it's a span/div inside an h2/h3, get parent. If it is the h2/h3, use it.
            if plot_id.name in ['h2', 'h3']:
                heading_tag = plot_id
            else:
                heading_tag = plot_id.find_parent(['h2', 'h3'])
        
        # Strategy 2: Look for h2/h3 with text "Plot" or "Synopsis"
        if not heading_tag:
            for h in soup.find_all(['h2', 'h3']):
                text = h.get_text(strip=True)
                if 'Plot' in text or 'Synopsis' in text:
                    heading_tag = h
                    break
        
        if not heading_tag:
            return "Plot not found."
            
        # Check if heading is wrapped in a div (e.g., mw-heading)
        # Recent Wikipedia change wraps h2 in <div class="mw-heading mw-heading2">
        parent = heading_tag.parent
        if parent and parent.name == 'div' and ('mw-heading' in parent.get('class', [])):
            heading_tag = parent
            
        plot_text = []
        # Get all paragraphs after the heading until the next heading
        for sibling in heading_tag.find_next_siblings():
            # Stop if we hit the next section header (h2, h3 or div.mw-heading)
            if sibling.name in ['h2', 'h3']:
                break
            if sibling.name == 'div' and ('mw-heading' in sibling.get('class', [])):
                break
                
            if sibling.name == 'p':
                plot_text.append(sibling.get_text(strip=True))
                
        return "\n\n".join(plot_text)

# Example usage
if __name__ == "__main__":
    scraper = WikipediaMovieScraper()
    movie_name = "Inception"
    print(f"Searching for {movie_name}...")
    url = scraper.search_movie(movie_name)
    
    if url:
        print(f"Found URL: {url}")
        details = scraper.scrape_details(url)
        if details:
            print("\n--- Move Details ---")
            print(f"Title: {details['title']}")
            print("\n[Infobox]")
            for k, v in details['infobox'].items():
                print(f"{k}: {v}")
            print("\n[Plot]")
            print(details['plot'][:500] + "..." if len(details['plot']) > 500 else details['plot'])
    else:
        print("Movie not found.")
