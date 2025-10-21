import os
import json
import argparse
from deep_translator import GoogleTranslator

def load_english_settings(file_path):
    """Load the English language settings file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def translate_text(translator, text, target_language):
    """Translate a single text string to the target language."""
    try:
        # Translate the text
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return text  # Return original text if translation fails

def translate_settings(english_settings, target_language):
    """Translate all settings to the target language."""
    translated_settings = {}
    
    print(f"Translating settings to {target_language}...")
    
    for key, value in english_settings.items():
        print(f"Translating: {key}")
        try:
            # Create translator for each translation to avoid rate limiting
            translator = GoogleTranslator(source='en', target=target_language)
            translated_value = translate_text(translator, value, target_language)
            translated_settings[key] = translated_value
        except Exception as e:
            print(f"Error translating key '{key}': {e}")
            translated_settings[key] = value  # Keep original if translation fails
    
    return translated_settings

def save_translated_settings(translated_settings, output_path):
    """Save the translated settings to a new JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated_settings, f, indent=2, ensure_ascii=False)
    
    print(f"Translated settings saved to: {output_path}")

def get_language_code(language_name):
    """Convert language name to language code for Google Translate."""
    language_codes = {
        'spanish': 'es',
        'french': 'fr',
        'german': 'de',
        'italian': 'it',
        'portuguese': 'pt',
        'dutch': 'nl',
        'russian': 'ru',
        'chinese': 'zh',
        'japanese': 'ja',
        'korean': 'ko',
        'arabic': 'ar',
        'hindi': 'hi',
        'turkish': 'tr',
        'polish': 'pl',
        'swedish': 'sv',
        'norwegian': 'no',
        'danish': 'da',
        'finnish': 'fi',
        'greek': 'el',
        'hebrew': 'he',
        'thai': 'th',
        'vietnamese': 'vi',
        'czech': 'cs',
        'hungarian': 'hu',
        'romanian': 'ro',
        'bulgarian': 'bg',
        'croatian': 'hr',
        'slovak': 'sk',
        'slovenian': 'sl',
        'estonian': 'et',
        'latvian': 'lv',
        'lithuanian': 'lt',
        'ukrainian': 'uk',
        'catalan': 'ca',
        'basque': 'eu',
        'galician': 'gl',
        'maltese': 'mt',
        'irish': 'ga',
        'welsh': 'cy',
        'icelandic': 'is'
    }
    
    return language_codes.get(language_name.lower(), language_name.lower())

def main():
    parser = argparse.ArgumentParser(description="Generate translated language settings files.")
    parser.add_argument("--language", required=True, help="Target language name (e.g., 'spanish', 'french', 'german')")
    parser.add_argument("--input", default="../app_languages/en.json", help="Path to the English settings file")
    parser.add_argument("--output-dir", default="../app_languages", help="Output directory for translated files")
    
    args = parser.parse_args()
    
    # Get language code for translation
    language_code = get_language_code(args.language)
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        return
    
    # Load English settings
    try:
        english_settings = load_english_settings(args.input)
        print(f"Loaded {len(english_settings)} settings from {args.input}")
    except Exception as e:
        print(f"Error loading English settings: {e}")
        return
    
    # Generate output file path
    output_filename = f"{language_code}.json"
    output_path = os.path.join(args.output_dir, output_filename)
    
    # Check if output file already exists
    if os.path.exists(output_path):
        response = input(f"File '{output_path}' already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Translation cancelled.")
            return
    
    # Translate settings
    try:
        translated_settings = translate_settings(english_settings, language_code)
        
        # Save translated settings
        save_translated_settings(translated_settings, output_path)
        
        print(f"\nTranslation completed successfully!")
        print(f"Created: {output_path}")
        print(f"Language: {args.language} ({language_code})")
        print(f"Translated {len(translated_settings)} settings")
        
    except Exception as e:
        print(f"Error during translation: {e}")

if __name__ == "__main__":
    main()