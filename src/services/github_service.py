import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GitHubService:
    def __init__(self):
        self.github_pat = os.getenv("GITHUB_PAT")
        self.repo_url = "https://api.github.com/repos/DKeAlvaro/llmers-langs/contents/"
        self.headers = {
            "Authorization": f"token {self.github_pat}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_available_languages(self):
        """
        Fetches the available UI languages and target languages from the GitHub repository.
        """
        ui_languages = self._get_languages_from_dir("app_languages")
        target_languages = self._get_languages_from_dir("lessons")
        return ui_languages, target_languages

    def _get_languages_from_dir(self, directory):
        """
        Helper function to get languages from a specific directory in the repo.
        """
        url = self.repo_url + directory
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        files = response.json()
        
        languages = []
        for file in files:
            if directory == "app_languages" and file['type'] == 'file' and file['name'].endswith('.json'):
                languages.append(file['name'].replace('.json', ''))
            elif directory == "lessons" and file['type'] == 'dir':
                languages.append(file['name'])
        return languages

    def download_file(self, download_url, save_path):
        """
        Downloads a single file from a given download_url.
        """
        response = requests.get(download_url, headers=self.headers)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)

    def download_language_files(self, ui_lang, target_lang_folder):
        """
        Downloads the selected UI language file and the entire folder for the target lesson language.
        """
        # Download UI language file
        ui_file_url = f"{self.repo_url}app_languages/{ui_lang}.json"
        ui_file_response = requests.get(ui_file_url, headers=self.headers).json()
        self.download_file(ui_file_response['download_url'], f"app_languages/{ui_lang}.json")

        # Download lesson files
        # First, get the language combination folder (e.g., en-es)
        lesson_folders_url = f"{self.repo_url}lessons/{target_lang_folder}"
        lesson_folders_response = requests.get(lesson_folders_url, headers=self.headers).json()
        
        for folder in lesson_folders_response:
            if folder['type'] == 'dir':
                lesson_lang_combination = folder['name']
                files_url = f"{self.repo_url}lessons/{target_lang_folder}/{lesson_lang_combination}"
                files_response = requests.get(files_url, headers=self.headers).json()
                for file in files_response:
                    if file['type'] == 'file' and file['name'].endswith('.json'):
                        save_path = f"lessons/{target_lang_folder}/{lesson_lang_combination}/{file['name']}"
                        self.download_file(file['download_url'], save_path)
