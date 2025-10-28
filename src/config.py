# config.py
import os
import json
from dotenv import load_dotenv
from src.managers.user_data_manager import user_data_manager

load_dotenv()

# --- LLM Configuration ---
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
OPENAI_BASE_URL="https://api.openai.com"

BASE_URL = DEEPSEEK_BASE_URL
MODEL = "deepseek-chat"

# --- Unified Language Configuration ---
# This single setting controls both UI language and lesson language
# Format: "ui_language-target_language" (e.g., "en-es" for English UI + English->Spanish lessons)
DEFAULT_LANGUAGE = "en-nl"  # Change this to switch between language combinations

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
def get_user_api_key():
    """Get user's saved API key"""
    return user_data_manager.get_setting('deepseek_api_key')

def save_user_api_key(api_key):
    """Save user's API key"""
    user_data_manager.set_setting('deepseek_api_key', api_key)

def clear_user_api_key():
    """Clear user's saved API key"""
    user_data_manager.set_setting('deepseek_api_key', None)

# This will hold the API key provided by the user at runtime
_runtime_api_key = None

def update_runtime_api_key(api_key: str):
    """Update the API key at runtime."""
    global _runtime_api_key
    _runtime_api_key = api_key

def get_user_api_key():
    """Get user's saved API key"""
    return user_data_manager.get_setting('deepseek_api_key')

def save_user_api_key(api_key):
    """Save user's API key"""
    user_data_manager.set_setting('deepseek_api_key', api_key)

def clear_user_api_key():
    """Clear user's saved API key"""
    user_data_manager.set_setting('deepseek_api_key', None)

def get_effective_api_key():
    """Get the effective API key, prioritizing the user's saved key over environment variables."""
    # Highest priority: runtime key
    if _runtime_api_key:
        return _runtime_api_key
    
    user_key = get_user_api_key()
    if user_key:
        return user_key
    
    # Fallback to environment variables if no user key is set
    return os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")


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