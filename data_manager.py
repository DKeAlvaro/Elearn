# data_manager.py
import json
import os
import config

class DataManager:
    def __init__(self):
        """Initialize DataManager with current language configuration"""
        self.lessons_folder = config.get_lessons_folder()
        self.lessons_file = os.path.join(self.lessons_folder, "lessons.json")
        self.lessons_data = self.load_lessons()
    
    def load_lessons(self):
        """Carga las lecciones desde el archivo JSON específico del idioma."""
        try:
            with open(self.lessons_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Lessons file not found: {self.lessons_file}")
            return {"lessons": []}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.lessons_file}: {e}")
            return {"lessons": []}
    
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