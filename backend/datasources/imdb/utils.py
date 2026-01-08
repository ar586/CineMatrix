
def parse_numeric(value):
    """
    Parse numeric strings like "1,000" -> 1000.
    Returns None if invalid.
    """
    if not value or value == "N/A":
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None
