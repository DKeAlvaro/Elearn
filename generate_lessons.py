import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Missing GEMINI_API_KEY. Create a .env with GEMINI_API_KEY=<your_key> or set it in your environment.")
    raise SystemExit(1)

# Configure the Gemini client
genai.configure(api_key=api_key)

# Use the Gemini 2.5 Pro model
model = genai.GenerativeModel("gemini-2.5-pro")
response = model.generate_content("Explain how AI works in a few words")

print(response.text)