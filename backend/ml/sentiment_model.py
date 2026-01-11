
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy.special import softmax
import numpy as np

class RobertaSentiment:
    def __init__(self, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.labels = ["negative", "neutral", "positive"]
        except Exception as e:
            print(f"Error loading Roberta model: {e}")
            self.model = None

    def predict(self, text):
        """
        Returns label, score, and confidence.
        """
        if not self.model:
            return "neutral", 0.0, 0.0

        encoded_input = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        
        top_label = self.labels[ranking[0]]
        confidence = float(scores[ranking[0]])
        
        # Calculate a single scalar score (-1 to 1)
        # negative index 0, neutral 1, positive 2
        # weighted sum: -1*neg + 0*neu + 1*pos
        scalar_score = (-1 * scores[0]) + (0 * scores[1]) + (1 * scores[2])

        return top_label, float(scalar_score), confidence
