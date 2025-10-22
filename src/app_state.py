# app_state.py
import src.config as config
from src.data_manager import DataManager
from src.managers.progress_manager import ProgressManager
from src.state.lesson_state import LessonState
from src.state.scenario_state import ScenarioState

class AppState:
    """Gestiona el estado global de la aplicación."""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.progress_manager = ProgressManager()
        self.lesson_state = LessonState(data_manager, self.progress_manager)
        self.scenario_state = ScenarioState()
        self.current_theme_index = 0
        self.has_premium = False
        self.user = None

    def update_premium_status(self, has_premium: bool):
        self.has_premium = has_premium

    def is_lesson_unlocked(self, lesson_id: str) -> bool:
        """Verifica si una lección está desbloqueada, considerando el estado premium."""
        lessons = self.data_manager.get_lessons()
        
        current_lesson_index = -1
        for i, lesson in enumerate(lessons):
            if lesson.get("id") == lesson_id:
                current_lesson_index = i
                break
        
        if current_lesson_index == -1:
            return False
        
        if current_lesson_index == 0:
            return True
        
        lesson_number = current_lesson_index + 1
        if not self.has_premium and lesson_number % 4 == 0:
            return False
        
        for i in range(current_lesson_index - 1, -1, -1):
            previous_lesson = lessons[i]
            previous_lesson_number = i + 1
            previous_lesson_id = previous_lesson.get("id")
            
            if not self.has_premium and previous_lesson_number % 4 == 0:
                continue
            
            return self.progress_manager.is_lesson_completed(previous_lesson_id)
        
        return True

    def get_lesson_lock_reason(self, lesson_id: str) -> str:
        """Returns the reason why a lesson is locked: 'unlocked', 'premium', or 'progression'."""
        lessons = self.data_manager.get_lessons()
        
        current_lesson_index = -1
        for i, lesson in enumerate(lessons):
            if lesson.get("id") == lesson_id:
                current_lesson_index = i
                break
        
        if current_lesson_index == -1:
            return "progression"
        
        if current_lesson_index == 0:
            return "unlocked"
        
        lesson_number = current_lesson_index + 1
        if not self.has_premium and lesson_number % 4 == 0:
            return "premium"
        
        for i in range(current_lesson_index - 1, -1, -1):
            previous_lesson = lessons[i]
            previous_lesson_number = i + 1
            previous_lesson_id = previous_lesson.get("id")
            
            if not self.has_premium and previous_lesson_number % 4 == 0:
                continue
            
            if self.progress_manager.is_lesson_completed(previous_lesson_id):
                return "unlocked"
            else:
                return "progression"
        
        return "unlocked"
