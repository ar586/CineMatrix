import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import backend.config # Load env
from ml.pipelines.sentiment_engine import SentimentEngine

def test_hybrid():
    print("🚀 Initializing Hybrid Sentiment Engine...")
    engine = SentimentEngine()
    
    # Text likely to confuse simple models (Ambiguous / Sarcastic / Mixed)
    # "It wasn't exactly terrible, but I wouldn't watch it again if you paid me."
    # This usually gets low confidence negative or neutral from simple models.
    ambiguous_text = "It wasn't exactly terrible, but I wouldn't watch it again if you paid me."
    
    print(f"\n📝 Analyzing Ambiguous Text: '{ambiguous_text}'")
    result = engine.analyze(ambiguous_text)
    
    print("\n🔍 Final Result:")
    print(result)

    if result.confidence > 0.85:
        print("\nNote: Local model was very confident. LLM might NOT have been triggered.")
    else:
        print("\nNote: Low local confidence. LLM should have been triggered (check logs).")

if __name__ == "__main__":
    test_hybrid()
