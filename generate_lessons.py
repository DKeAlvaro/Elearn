import os
import argparse
import json
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

def parse_lesson_plan(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lessons = content.split('**Lesson ')[1:]
    lesson_descriptions = []
    for lesson in lessons:
        lesson_descriptions.append("**Lesson " + lesson)
    return lesson_descriptions

def generate_lesson(target_lang, lesson_description, prompt_template):
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


def main():
    parser = argparse.ArgumentParser(description="Generate language lessons.")
    parser.add_argument("--language", help="Specify the language to generate lessons for (e.g., 'dutch').")
    args = parser.parse_args()

    lessons_base_dir = "lessons"
    languages_file = os.path.join(lessons_base_dir, "languages.txt")
    lesson_plan_file = os.path.join(lessons_base_dir, "lesson_plan.md")
    prompt_file = os.path.join(lessons_base_dir, "prompts", "create_lesson.md")

    with open(languages_file, 'r', encoding='utf-8') as f:
        languages = [line.strip().split('-') for line in f.readlines()]

    lesson_descriptions = parse_lesson_plan(lesson_plan_file)

    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    target_languages = []
    if args.language:
        for lang_name, lang_code in languages:
            if args.language.lower() == lang_name.lower():
                target_languages.append((lang_name, lang_code))
                break
        if not target_languages:
            print(f"Language '{args.language}' not found in {languages_file}")
            return
    else:
        target_languages = languages

    for lang_name, lang_code in target_languages:
        print(f"Processing language: {lang_name}")
        output_dir = os.path.join(lessons_base_dir, lang_name, f"en-{lang_code}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

        for i, lesson_desc in enumerate(lesson_descriptions):
            lesson_num = i + 1
            print(f"Generating lesson {lesson_num} for {lang_name}...")
            lesson_json = generate_lesson(lang_name, lesson_desc, prompt_template)

            if lesson_json:
                output_file = os.path.join(output_dir, f"lesson_{lesson_num}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(lesson_json, f, indent=2, ensure_ascii=False)
                print(f"Successfully generated and saved {output_file}")

if __name__ == "__main__":
    main()