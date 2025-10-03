import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not set.")
else:
    genai.configure(api_key=api_key)
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)
