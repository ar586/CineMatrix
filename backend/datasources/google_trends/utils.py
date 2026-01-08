
def format_timeframe(period):
    """
    Validate and format timeframe strings.
    For now, pass-through, but can be extended to map '5y' -> 'today 5-y'.
    """
    valid_prefixes = ['now', 'today', 'all']
    # Minimal validation/mapping
    return period
