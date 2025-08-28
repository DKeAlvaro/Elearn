# app_state.py
from data_manager import DataManager
import json
import os

class AppState:
    """Gestiona el estado global de la aplicación."""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_lesson_id = None
        self.current_slide_index = 0
        self.current_theme_index = 0 # Nuevo
        self.completed_lessons = set()  # Track completed lessons
        self.progress_file = "progress.json"  # File to persist progress
        self.load_progress()

    def select_lesson(self, lesson_id: str):
        """Selecciona una lección para empezar."""
        self.current_lesson_id = lesson_id
        self.current_slide_index = 0

    def next_slide(self):
        """Avanza a la siguiente diapositiva. Devuelve True si es posible, False si la lección ha terminado."""
        content = self.data_manager.get_lesson_content(self.current_lesson_id)
        if self.current_slide_index < len(content) - 1:
            self.current_slide_index += 1
            return True
        return False

    def previous_slide(self):
        """Retrocede a la diapositiva anterior. Devuelve True si es posible, False si ya está en la primera."""
        if self.current_slide_index > 0:
            self.current_slide_index -= 1
            return True
        return False

    def get_current_slide_data(self):
        """Obtiene los datos de la diapositiva actual."""
        if self.current_lesson_id:
            content = self.data_manager.get_lesson_content(self.current_lesson_id)
            if 0 <= self.current_slide_index < len(content):
                return content[self.current_slide_index]
        return None

    def get_current_lesson_title(self) -> str:
        """Obtiene el título de la lección actual."""
        if self.current_lesson_id:
            lesson = self.data_manager.get_lesson_by_id(self.current_lesson_id)
            return lesson.get("title", "Lección") if lesson else "Lección"
        return "Lección"

    
    def mark_lesson_completed(self, lesson_id: str):
        """Marca una lección como completada."""
        self.completed_lessons.add(lesson_id)
        self.save_progress()
    
    def is_lesson_completed(self, lesson_id: str) -> bool:
        """Verifica si una lección está completada."""
        return lesson_id in self.completed_lessons
    
    def load_progress(self):
        """Carga el progreso desde el archivo."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_lessons = set(data.get('completed_lessons', []))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading progress: {e}")
            self.completed_lessons = set()
    
    def save_progress(self):
        """Guarda el progreso al archivo."""
        try:
            data = {
                'completed_lessons': list(self.completed_lessons)
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")