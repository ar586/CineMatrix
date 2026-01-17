
class DiscussionBuilder:
    def __init__(self):
        pass

    def build_text(self, item: dict, source_type: str) -> str:
        """
        Combines title, body, and comments into a single text block.
        """
        text_parts = []
        
        if source_type == "reddit":
            text_parts.append(item.get("title", ""))
            text_parts.append(item.get("selftext", ""))
            # If comments are attached as a list of strings or objects
            if "comments" in item:
                # Assuming simple list of strings for now, or parsing deep objects if needed
                # For simplified ingestion, we assume ingestion layer passed relevant text
                comments = item["comments"]
                if isinstance(comments, list):
                    text_parts.extend([str(c) for c in comments[:5]]) # Top 5 comments

        elif source_type == "youtube":
            text_parts.append(item.get("title", ""))
            text_parts.append(item.get("description", ""))
            if item.get("transcript"):
                 text_parts.append(item.get("transcript"))
            if "comments" in item:
                comments = item["comments"]
                if isinstance(comments, list):
                    text_parts.extend([str(c) for c in comments[:5]])

        return " ".join([t for t in text_parts if t]).strip()
