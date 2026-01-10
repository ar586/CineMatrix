
class SentimentSignal:
    def __init__(self):
        pass

    def analyze(self, text: str, source: str, source_ref: dict) -> dict:
        """
        Analyze sentiment from text data.
        Returns a dict matching the SentimentAnalysis schema input.
        """
        # Basic heuristic for MVP (since no heavy NLP lib is installed)
        # In production, swap this with VADER or an LLM call.
        
        words = text.lower().split()
        positive_words = {"good", "great", "amazing", "awesome", "love", "excellent", "best", "masterpiece"}
        negative_words = {"bad", "terrible", "worst", "hate", "boring", "awful", "trash", "disappointing"}
        
        score = 0
        for word in words:
            if word in positive_words:
                score += 0.1
            elif word in negative_words:
                score -= 0.1
        
        # Clamp score between -1 and 1
        score = max(-1.0, min(1.0, score))
        
        label = "neutral"
        if score > 0.05:
            label = "positive"
        elif score < -0.05:
            label = "negative"
            
        return {
            "sentiment": {
                "label": label,
                "score": round(score, 2),
                "confidence": 0.8  # Placeholder confidence
            },
            "aspects": {
                "general": round(score, 2)
            }
        }
