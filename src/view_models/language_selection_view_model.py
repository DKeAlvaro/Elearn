from src.services.github_service import GitHubService
import src.config as config
from src.managers.user_data_manager import user_data_manager

class LanguageSelectionViewModel:
    def __init__(self, on_complete):
        self.github_service = GitHubService()
        self.on_complete = on_complete

    async def get_available_languages(self):
        try:
            return await self.github_service.get_available_languages()
        except Exception as e:
            print(f"Error getting available languages: {e}")
            return [], []

    async def download_languages(self, ui_lang, target_lang_folder):
        try:
            await self.github_service.download_language_files("en", target_lang_folder)
            
            target_lang_code = self._get_target_lang_code(target_lang_folder)
            if target_lang_code:
                lang_combination = f"en-{target_lang_code}"
                config.set_default_language(lang_combination)
                user_data_manager.set_setting("selected_language", lang_combination)
                config.load_language()
            
            self.on_complete()
        except Exception as e:
            print(f"Error downloading languages: {e}")
            
    def _get_target_lang_code(self, target_lang_folder):
        language_folder_map = {
            'english': 'en',
            'french': 'fr',
            'spanish': 'es',
            'german': 'de',
            'japanese': 'ja',
            'italian': 'it',
            'korean': 'ko',
            'chinese': 'zh',
            'russian': 'ru',
            'portuguese': 'pt',
            'arabic': 'ar',
            'hindi': 'hi',
            'turkish': 'tr',
            'dutch': 'nl',
            'swedish': 'sv'
        }
        return language_folder_map.get(target_lang_folder.lower())
