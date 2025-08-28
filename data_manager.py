# data_manager.py
import json

class DataManager:
    """Carga y gestiona el acceso a los datos de las lecciones desde un JSON."""
    def __init__(self, json_path: str):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error cargando el JSON: {e}")
            self.data = {}

    def get_lessons(self):
        """Devuelve la lista de todas las lecciones."""
        return self.data.get('lessons', [])

    def get_lesson_by_id(self, lesson_id: str):
        """Encuentra una lección por su ID."""
        for lesson in self.get_lessons():
            if lesson['id'] == lesson_id:
                return lesson
        return None

    def get_lesson_content(self, lesson_id: str):
        """Devuelve el contenido (diapositivas) de una lección específica."""
        lesson = self.get_lesson_by_id(lesson_id)
        return lesson.get('content', []) if lesson else []
    
    # +++ NEW METHOD +++
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