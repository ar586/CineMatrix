import sys
import os
sys.path.append(os.getcwd())

print("1. Importing LangGraph...")
try:
    from langgraph.graph import StateGraph
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("2. Importing Reddit Agent...")
try:
    from agents.nodes.reddit_node import reddit_agent_node
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("3. Importing Transformers...")
try:
    import transformers
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("4. Importing Sentiment Engine (Heavy)...")
try:
    from ml.pipelines.sentiment_engine import SentimentEngine
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("Done.")
