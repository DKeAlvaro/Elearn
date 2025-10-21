import os
import json
import argparse
from generate_lessons.make_api_call import initialize_gemini_client

def fix_lesson_structure(model, file_path):
    """Fix the structure of a lesson file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lesson_content = f.read()

    prompt = (
        f"Please fix the following JSON lesson file. The 'title' element should be a direct child of the conversation_flow step, not nested inside 'user_response'.\n\n"
        f"Here is the content of the file:\n\n{lesson_content}"
    )

    print(f"Fixing lesson: {file_path}...")

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        
        # Overwrite the existing file with the corrected content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_text)
        
        print(f"Successfully fixed and saved {file_path}")
        return True
    except Exception as e:
        print(f"Error fixing lesson {file_path}: {e}")
        print("Response was:", response.text if 'response' in locals() else "No response")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix the structure of a lesson JSON file.")
    parser.add_argument("file_path", type=str, help="The path to the lesson file to fix, relative to the 'lessons' directory.")
    args = parser.parse_args()

    model = initialize_gemini_client()
    
    # Construct the full path to the lesson file
    lessons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lessons')
    full_file_path = os.path.join(lessons_dir, args.file_path)

    if not os.path.exists(full_file_path):
        print(f"Error: The file {full_file_path} does not exist.")
    else:
        fix_lesson_structure(model, full_file_path)