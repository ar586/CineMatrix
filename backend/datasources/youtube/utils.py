
import re

def parse_duration(duration_str):
    """
    Parse ISO 8601 duration string (e.g., PT1H2M10S) to readable string (1:02:10).
    """
    try:
        # Regex to capture Hours, Minutes, Seconds
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration_str)
        
        if not match:
            return duration_str
            
        h, m, s = match.groups()
        h = int(h) if h else 0
        m = int(m) if m else 0
        s = int(s) if s else 0
        
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"
    except Exception:
        return duration_str
