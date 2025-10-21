import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def initialize_gemini_client():
    """Initialize and configure the Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Missing GEMINI_API_KEY. Create a .env with GEMINI_API_KEY=<your_key> or set it in your environment.")
        raise SystemExit(1)
    
    # Configure the Gemini client
    genai.configure(api_key=api_key)
    
    # Use the Gemini 2.5 Pro model
    return genai.GenerativeModel("gemini-2.5-pro")

def make_api_call(model, target_lang, lesson_description, prompt_template):
    """Make an API call to generate lesson content."""
    print(f"Generating lesson for {target_lang}...")
    prompt = prompt_template.replace("{TARGET_LANG}", target_lang).replace("{LESSON_DESCRIPTION}", lesson_description)
    
    try:
        response = model.generate_content(prompt)
        # Extracting the JSON part from the response text
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        
        return json.loads(json_text)
    except Exception as e:
        print(f"Error generating lesson for {target_lang}: {e}")
        print("Response was:", response.text)
        return None