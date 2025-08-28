# config.py
import os
import json
from dotenv import load_dotenv

load_dotenv()

# --- Configuración del LLM ---
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# --- Unified Language Configuration ---
# This single setting controls both UI language and lesson language
# Available options: "es-nl" (Spanish UI + Spanish->Dutch lessons) or "en-nl" (English UI + English->Dutch lessons)
DEFAULT_LANGUAGE = "en-nl"  # Change this to switch between language combinations

LANGUAGE_DIR = "app_languages"

# Language configuration mapping
LANGUAGE_CONFIG = {
    "es-nl": {
        "name": "Español -> Neerlandés",
        "ui_language": "es",  # Spanish UI
        "learning_language": "Español",
        "target_language": "Neerlandés",
        "lessons_folder": "lessons/es-nl"
    },
    "en-nl": {
        "name": "English -> Dutch",
        "ui_language": "en",  # English UI
        "learning_language": "English", 
        "target_language": "Dutch",
        "lessons_folder": "lessons/en-nl"
    }
}

# Global language strings variable
_language_strings = {}

def get_current_config():
    """Get current language configuration"""
    return LANGUAGE_CONFIG.get(DEFAULT_LANGUAGE, LANGUAGE_CONFIG["es-nl"])

def load_language():
    """Load language strings from JSON file based on current configuration"""
    global _language_strings
    config = get_current_config()
    ui_language = config["ui_language"]
    
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
    config = get_current_config()
    return config["lessons_folder"]

def get_language_info():
    """Get current language information"""
    return get_current_config()

# Initialize with default language
load_language()

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

