import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import backend.config # Load env
from backend.llm.client import LLMService

def test():
    print("Initializing LLM Service...")
    service = LLMService()
    
    print("\n--- Listing Models ---")
    try:
        import google.generativeai as genai
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"List Models Error: {e}")

    print("\n--- Test 1: Chat ---")
    res = service.generate_text("Explain what a 'MacGuffin' is in movies in one sentence.")
    print(f"Response: {res}")
    
    print("\n--- Test 2: JSON ---")
    json_res = service.generate_json("Generate a JSON object for a movie character with 'name' and 'role'.")
    print(f"JSON Response: {json_res}")

    if res and json_res:
        print("\n✅ LLM Integration Verified!")
    else:
        print("\n❌ One or more tests failed.")

if __name__ == "__main__":
    test()
