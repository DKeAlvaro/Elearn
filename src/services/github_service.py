import os
import httpx
import asyncio
import aiofiles
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

    async def get_available_languages(self):
        """
        Fetches the available UI languages and target languages from the GitHub repository asynchronously.
        """
        async with httpx.AsyncClient() as client:
            ui_languages_task = self._get_languages_from_dir(client, "app_languages")
            target_languages_task = self._get_languages_from_dir(client, "lessons")
            ui_languages, target_languages = await asyncio.gather(ui_languages_task, target_languages_task)
            return ui_languages, target_languages

    async def _get_languages_from_dir(self, client: httpx.AsyncClient, directory: str):
        """
        Helper function to get languages from a specific directory in the repo asynchronously.
        """
        url = self.repo_url + directory
        response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        files = response.json()
        
        languages = []
        for file in files:
            if directory == "app_languages" and file['type'] == 'file' and file['name'].endswith('.json'):
                languages.append(file['name'].replace('.json', ''))
            elif directory == "lessons" and file['type'] == 'dir':
                languages.append(file['name'])
        return languages

    async def download_file(self, client: httpx.AsyncClient, download_url: str, save_path: str):
        """
        Downloads a single file from a given download_url asynchronously.
        """
        response = await client.get(download_url, headers=self.headers)
        response.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(response.content)

    async def download_language_files(self, ui_lang: str, target_lang_folder: str):
        """
        Downloads the selected UI language file and the entire folder for the target lesson language asynchronously.
        """
        async with httpx.AsyncClient() as client:
            # Download UI language file
            ui_file_url = f"{self.repo_url}app_languages/{ui_lang}.json"
            ui_file_response = await client.get(ui_file_url, headers=self.headers)
            ui_file_response.raise_for_status()
            await self.download_file(client, ui_file_response.json()['download_url'], f"app_languages/{ui_lang}.json")

            # Download lesson files
            lesson_folders_url = f"{self.repo_url}lessons/{target_lang_folder}"
            lesson_folders_response = await client.get(lesson_folders_url, headers=self.headers)
            lesson_folders_response.raise_for_status()
            
            tasks = []
            for folder in lesson_folders_response.json():
                if folder['type'] == 'dir':
                    lesson_lang_combination = folder['name']
                    files_url = f"{self.repo_url}lessons/{target_lang_folder}/{lesson_lang_combination}"
                    files_response = await client.get(files_url, headers=self.headers)
                    files_response.raise_for_status()
                    for file in files_response.json():
                        if file['type'] == 'file' and file['name'].endswith('.json'):
                            save_path = f"lessons/{target_lang_folder}/{lesson_lang_combination}/{file['name']}"
                            task = self.download_file(client, file['download_url'], save_path)
                            tasks.append(task)
            
            await asyncio.gather(*tasks)