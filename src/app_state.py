# app_state.py
import src.config as config
from src.managers.data_manager import DataManager
from src.managers.progress_manager import ProgressManager
from src.state.lesson_state import LessonState
from src.state.scenario_state import ScenarioState

class AppState:
    """Manages the global state of the application."""
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.progress_manager = ProgressManager()
        self.lesson_state = LessonState(data_manager, self.progress_manager)
        self.scenario_state = ScenarioState()
        self.current_theme_index = 0

    def reload_lessons(self):
        """Reloads the lessons in the data manager."""
        self.data_manager.reload_lessons()

    def is_lesson_unlocked(self, lesson_id: str) -> bool:
        """Verifies if a lesson is unlocked."""
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
        
        # Check if the previous lesson is completed
        previous_lesson = lessons[current_lesson_index - 1]
        previous_lesson_id = previous_lesson.get("id")
        return self.progress_manager.is_lesson_completed(previous_lesson_id)

    def get_lesson_lock_reason(self, lesson_id: str) -> str:
        """Returns the reason why a lesson is locked: 'unlocked' or 'progression'."""
        if self.is_lesson_unlocked(lesson_id):
            return "unlocked"
        else:
            return "progression"
