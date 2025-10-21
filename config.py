# config.py
import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- Configuración del LLM ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# User settings file
USER_SETTINGS_FILE = "user_settings.json"

# Runtime API key (can be updated by user)
_runtime_api_key = None

# --- Unified Language Configuration ---
# This single setting controls both UI language and lesson language
# Format: "ui_language-target_language" (e.g., "en-es" for English UI + English->Spanish lessons)
DEFAULT_LANGUAGE = "en-es"  # Change this to switch between language combinations

LANGUAGE_DIR = "app_languages"

# Global language strings variable
_language_strings = {}

def get_ui_language():
    """Extract UI language from DEFAULT_LANGUAGE (part before the dash)"""
    return DEFAULT_LANGUAGE.split('-')[0]

def get_target_language_folder():
    """Get target language folder name based on DEFAULT_LANGUAGE"""
    target_code = DEFAULT_LANGUAGE.split('-')[1]
    # Map language codes to folder names
    language_folder_map = {
        'en': 'english',
        'fr': 'french',
        'es': 'spanish',
        'de': 'german',
        'ja': 'japanese',
        'it': 'italian',
        'ko': 'korean',
        'zh': 'chinese',
        'ru': 'russian',
        'pt': 'portuguese',
        'ar': 'arabic',
        'hi': 'hindi',
        'tr': 'turkish',
        'nl': 'dutch',
        'sv': 'swedish'
    }
    return language_folder_map.get(target_code, target_code)

def load_language():
    """Load language strings from JSON file based on current configuration"""
    global _language_strings
    ui_language = get_ui_language()
    
    try:
        language_file = os.path.join(LANGUAGE_DIR, f"{ui_language}.json")
        with open(language_file, 'r', encoding='utf-8') as f:
            _language_strings = json.load(f)
    except FileNotFoundError:
        print(f"Language file {language_file} not found. Using empty strings.")
        _language_strings = {}
    except Exception as e:
        print(f"Error loading language file: {e}")
        _language_strings = {}

def get_text(key: str, default: str = "") -> str:
    """Get localized text by key"""
    return _language_strings.get(key, default)

def get_lessons_folder():
    """Get the folder path for lessons based on current language configuration"""
    target_folder = get_target_language_folder()
    return f"lessons/{target_folder}/{DEFAULT_LANGUAGE}"

def get_language_info():
    """Get current language information"""
    ui_lang = get_ui_language()
    target_code = DEFAULT_LANGUAGE.split('-')[1]
    target_folder = get_target_language_folder()
    
    return {
        "ui_language": ui_lang,
        "target_language_code": target_code,
        "target_language_folder": target_folder,
        "lessons_folder": get_lessons_folder(),
        "language_combination": DEFAULT_LANGUAGE
    }

# Initialize with default language
load_language()

# --- User API Key Management ---
def load_user_settings():
    """Load user settings from file"""
    try:
        if os.path.exists(USER_SETTINGS_FILE):
            with open(USER_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading user settings: {e}")
    return {}

def save_user_settings(settings):
    """Save user settings to file"""
    try:
        with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving user settings: {e}")
        raise

def get_user_api_key():
    """Get user's saved API key"""
    settings = load_user_settings()
    return settings.get('deepseek_api_key')

def save_user_api_key(api_key):
    """Save user's API key"""
    settings = load_user_settings()
    settings['deepseek_api_key'] = api_key
    save_user_settings(settings)

def clear_user_api_key():
    """Clear user's saved API key"""
    settings = load_user_settings()
    if 'deepseek_api_key' in settings:
        del settings['deepseek_api_key']
    save_user_settings(settings)

def get_effective_api_key():
    """Get the effective API key (user's key takes precedence over environment)"""
    global _runtime_api_key
    if _runtime_api_key:
        return _runtime_api_key
    
    user_key = get_user_api_key()
    if user_key:
        return user_key
    
    return DEEPSEEK_API_KEY

def update_runtime_api_key(api_key):
    """Update the runtime API key"""
    global _runtime_api_key
    _runtime_api_key = api_key

# Initialize runtime API key with user's saved key if available
user_saved_key = get_user_api_key()
if user_saved_key:
    _runtime_api_key = user_saved_key

# --- Modern Material Design 3 Color Schemes ---
THEMES = [
    {
        "name": "Modern Purple",
        "bgcolor": "#FEFBFF",
        "primary": "#6750A4",
        "on_primary": "#FFFFFF",
        "secondary": "#625B71",
        "secondary_container": "#E8DEF8",
        "on_secondary_container": "#1D192B",
        "surface": "#FEFBFF",
        "surface_variant": "#E7E0EC",
        "on_surface_variant": "#49454F",
        "appbar_bgcolor": "#EADDFF",
        "card_color": "#FFFFFF",
        "shadow_color": "#000000"
    },
    {
        "name": "Ocean Blue",
        "bgcolor": "#FCFCFF",
        "primary": "#0061A4",
        "on_primary": "#FFFFFF",
        "secondary": "#535F70",
        "secondary_container": "#D7E3F7",
        "on_secondary_container": "#101C2B",
        "surface": "#FCFCFF",
        "surface_variant": "#DFE2EB",
        "on_surface_variant": "#43474E",
        "appbar_bgcolor": "#D0E4F7",
        "card_color": "#FFFFFF",
        "shadow_color": "#000000"
    },
    {
        "name": "Fresh Green",
        "bgcolor": "#FDFDF5",
        "primary": "#006E1C",
        "on_primary": "#FFFFFF",
        "secondary": "#52634F",
        "secondary_container": "#D4E8CF",
        "on_secondary_container": "#101F0F",
        "surface": "#FDFDF5",
        "surface_variant": "#DEE5D8",
        "on_surface_variant": "#424940",
        "appbar_bgcolor": "#D2E8D3",
        "card_color": "#FFFFFF",
        "shadow_color": "#000000"
    }
]

