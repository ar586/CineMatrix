
import isodate

def parse_duration(duration_str):
    """
    Parse ISO 8601 duration string (e.g., PT1H2M10S) to readable string (1:02:10).
    """
    try:
        dur = isodate.parse_duration(duration_str)
        return str(dur)
    except Exception:
        return duration_str
