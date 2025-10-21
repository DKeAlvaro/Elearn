import os
import argparse
import json
from generate_lessons.make_api_call import initialize_gemini_client, make_api_call

def parse_lesson_plan(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lessons = content.split('**Lesson ')[1:]
    lesson_descriptions = []
    for lesson in lessons:
        lesson_descriptions.append("**Lesson " + lesson)
    return lesson_descriptions




def main():
    parser = argparse.ArgumentParser(description="Generate language lessons.")
    parser.add_argument("--language", help="Specify the language to generate lessons for (e.g., 'dutch').")
    args = parser.parse_args()

    # Initialize the Gemini client
    model = initialize_gemini_client()

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
            output_file = os.path.join(output_dir, f"lesson_{lesson_num}.json")
            
            # Check if lesson already exists
            if os.path.exists(output_file):
                print(f"Skipping lesson {lesson_num} for {lang_name} - lesson_{lesson_num}.json already exists")
                continue
            
            print(f"Generating lesson {lesson_num} for {lang_name}...")
            lesson_json = make_api_call(model, lang_name, lesson_desc, prompt_template)

            if lesson_json:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(lesson_json, f, indent=2, ensure_ascii=False)
                print(f"Successfully generated and saved {output_file}")

if __name__ == "__main__":
    main()