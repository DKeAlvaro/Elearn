# user_data_manager.py
import json
import os

class UserDataManager:
    def __init__(self, file_path="user_data.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.file_path):
            return self._get_default_data()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_data()

    def _save_data(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")

    def _get_default_data(self):
        return {
            "settings": {},
            "progress": {
                "completed_lessons": [],
                "interactive_scenario_progress": {},
                "lesson_slide_positions": {},
                "user_data": {}
            },
            "app_data": {
                "first_run": True
            }
        }

    def get_setting(self, key, default=None):
        return self.data.get("settings", {}).get(key, default)

    def set_setting(self, key, value):
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self._save_data()

    def get_progress(self, key, default=None):
        return self.data.get("progress", {}).get(key, default)

    def set_progress(self, key, value):
        if "progress" not in self.data:
            self.data["progress"] = {}
        self.data["progress"][key] = value
        self._save_data()

    def get_app_data(self, key, default=None):
        return self.data.get("app_data", {}).get(key, default)

    def set_app_data(self, key, value):
        if "app_data" not in self.data:
            self.data["app_data"] = {}
        self.data["app_data"][key] = value
        self._save_data()

# Global instance
user_data_manager = UserDataManager()
