
import re

def clean_text(text):
    """
    Remove extra whitespace and basic cleanup.
    """
    if not text:
        return ""
    # Replace multiple newlines/spaces with single space (unless we want to preserve paragraph structure)
    # For general cleaning, we might want to keep newlines if it's a plot, but strip if it's a small field.
    # Let's simple strip valid whitespace for now.
    return text.strip()
