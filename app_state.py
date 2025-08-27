# app_state.py
from data_manager import DataManager
from config import THEMES

class AppState:
    """Gestiona el estado global de la aplicación."""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_lesson_id = None
        self.current_slide_index = 0
        self.current_theme_index = 0 # Nuevo

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

    def cycle_theme(self):
        """Cambia al siguiente tema de la lista."""
        self.current_theme_index = (self.current_theme_index + 1) % len(THEMES)