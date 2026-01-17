import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import google.generativeai as genai
from backend import config

# Configure API
genai.configure(api_key=config.GEMINI_API_KEY)

print("=" * 60)
print("Available Models in Google GenAI API:")
print("=" * 60)

for model in genai.list_models():
    if 'gemma' in model.name.lower():
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported Methods: {model.supported_generation_methods}")
