# data_manager.py
import json
import os
import config
from user_data_manager import user_data_manager

class DataManager:
    def __init__(self):
        """Initialize DataManager with current language configuration"""
        self.lessons_folder = config.get_lessons_folder()
        self.lessons_data = self.load_lessons()

    def is_first_run(self):
        """Checks if it's the first time the app is run."""
        return user_data_manager.get_app_data("first_run", True)

    def set_first_run_completed(self):
        """Marks the first run as completed."""
        user_data_manager.set_app_data("first_run", False)
    
    def load_lessons(self):
        """Loads lessons from individual JSON files in the language-specific folder."""
        lessons = []
        if not os.path.exists(self.lessons_folder):
            print(f"Lessons folder not found: {self.lessons_folder}")
            return {"lessons": []}

        for filename in os.listdir(self.lessons_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(self.lessons_folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lessons.append(json.load(file))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
                except Exception as e:
                    print(f"Error loading lesson from {file_path}: {e}")
        
        return {"lessons": lessons}
    
    def get_lessons(self):
        """Devuelve la lista de lecciones."""
        return self.lessons_data.get('lessons', [])
    
    def get_lesson_by_id(self, lesson_id: str):
        """Devuelve una lección específica por su ID."""
        for lesson in self.get_lessons():
            if lesson.get('id') == lesson_id:
                return lesson
        return None
    
    def get_lesson_content(self, lesson_id: str):
        """Devuelve el contenido (diapositivas) de una lección específica."""
        lesson = self.get_lesson_by_id(lesson_id)
        return lesson.get('content', []) if lesson else []
    
    def get_language_info(self):
        """Get language information from lessons file"""
        return self.lessons_data.get('language_info', {})
    
    def get_content_by_item_id(self, item_id: str) -> dict | None:
        """
        Encuentra el texto de un concepto específico a partir de su item_id.
        """
        for lesson in self.get_lessons():
            for content_item in lesson.get('content', []):
                if content_item.get('item_id') == item_id:
                    if content_item['type'] == 'vocabulary':
                        return list(content_item['data'].keys())[0]
                    elif content_item['type'] == 'expression':
                        return content_item['data']['phrase']
                    elif content_item['type'] == 'grammar':
                        # Para gramática, usamos el título como una palabra clave
                        return content_item['title']
        return None
