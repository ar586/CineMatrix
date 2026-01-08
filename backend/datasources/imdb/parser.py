
from .utils import parse_numeric

class IMDBParser:
    def parse_movie(self, data):
        """
        Parse raw OMDB JSON response.
        """
        if not data or data.get("Response") == "False":
            return None

        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "rated": data.get("Rated"),
            "released": data.get("Released"),
            "runtime": data.get("Runtime"),
            "genre": data.get("Genre", "").split(", "),
            "director": data.get("Director"),
            "actors": data.get("Actors", "").split(", "),
            "plot": data.get("Plot"),
            "language": data.get("Language"),
            "country": data.get("Country"),
            "awards": data.get("Awards"),
            "poster": data.get("Poster"),
            "imdb_rating": parse_numeric(data.get("imdbRating")),
            "imdb_votes": parse_numeric(data.get("imdbVotes")),
            "imdb_id": data.get("imdbID"),
            "box_office": data.get("BoxOffice"),
        }
