
from transformers import pipeline

class DebertaAspect:
    def __init__(self, model_name="facebook/bart-large-mnli"):
        # Using BART-large-mnli for zero-shot as it's the standard default and robust
        # You could swap for "cross-encoder/nli-deberta-v3-base" for better performance but slower
        try:
            self.classifier = pipeline("zero-shot-classification", model=model_name)
            self.aspect_labels = ["acting", "story", "ending", "music", "visuals", "pacing"]
        except Exception as e:
            print(f"Error loading Aspect model: {e}")
            self.classifier = None

    def extract_aspects(self, text):
        """
        Returns a dictionary of aspect scores.
        """
        if not self.classifier:
            return {}

        result = self.classifier(text, self.aspect_labels, multi_label=True)
        
        # result is like {'sequence': '...', 'labels': ['acting', ...], 'scores': [0.9, ...]}
        aspect_scores = {}
        for label, score in zip(result['labels'], result['scores']):
            # We treat the entailment score as the aspect sentiment/relevance
            # Note: Zero-shot classification gives relevance, not necessarily sentiment polarity.
            # To get SENTIMENT per aspect, we'd need aspect-based sentiment analysis (ABSA).
            # For this MVP, we will assume if the aspect is highly relevant, we need to associate the overall sentiment
            # or run a second pass. 
            # Reviewing the user request: "Aspect score (acting, story, etc)" usually implies sentiment.
            # Zero-shot classification helps find IF the aspect is mentioned.
            # We will use the score as "relevance".
            # To map to sentiment, typically one would run sentiment analysis on sentences containing the aspect.
            
            # Simple heuristic for MVP: Return relevance. The Aggregator can multiply by overall sentiment 
            # or we can refine this later to be proper ABSA.
            aspect_scores[label] = float(score)
            
        return aspect_scores
