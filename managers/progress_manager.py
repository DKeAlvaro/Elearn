# managers/progress_manager.py
import json
import os

class ProgressManager:
    def __init__(self, progress_file="progress.json"):
        self.progress_file = progress_file
        self.completed_lessons = set()
        self.interactive_scenario_progress = {}
        self.lesson_slide_positions = {}
        self.user_data = {}
        self.load_progress()

    def load_progress(self):
        """Carga el progreso desde el archivo."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_lessons = set(data.get('completed_lessons', []))
                    self.interactive_scenario_progress = data.get('interactive_scenario_progress', {})
                    self.lesson_slide_positions = data.get('lesson_slide_positions', {})
                    self.user_data = data.get('user_data', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading progress: {e}")
            self.completed_lessons = set()
            self.interactive_scenario_progress = {}
            self.lesson_slide_positions = {}
            self.user_data = {}

    def save_progress(self):
        """Guarda el progreso al archivo."""
        try:
            data = {
                'completed_lessons': list(self.completed_lessons),
                'interactive_scenario_progress': self.interactive_scenario_progress,
                'lesson_slide_positions': self.lesson_slide_positions,
                'user_data': self.user_data
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def mark_lesson_completed(self, lesson_id: str):
        """Marca una lección como completada."""
        self.completed_lessons.add(lesson_id)
        self.save_progress()

    def is_lesson_completed(self, lesson_id: str) -> bool:
        """Verifica si una lección está completada."""
        return lesson_id in self.completed_lessons

    def save_interactive_scenario_progress(self, lesson_id: str, scenario_id: str, completed_goals: set, current_goal_index: int, extracted_info: dict):
        """Guarda el progreso de un escenario interactivo."""
        if lesson_id not in self.interactive_scenario_progress:
            self.interactive_scenario_progress[lesson_id] = {}
        
        self.interactive_scenario_progress[lesson_id][scenario_id] = {
            'completed_goals': list(completed_goals),
            'current_goal_index': current_goal_index,
            'extracted_info': extracted_info
        }
        self.save_progress()

    def get_interactive_scenario_progress(self, lesson_id: str, scenario_id: str):
        """Obtiene el progreso de un escenario interactivo."""
        if lesson_id in self.interactive_scenario_progress and scenario_id in self.interactive_scenario_progress[lesson_id]:
            progress = self.interactive_scenario_progress[lesson_id][scenario_id]
            return {
                'completed_goals': set(progress.get('completed_goals', [])),
                'current_goal_index': progress.get('current_goal_index', 0),
                'extracted_info': progress.get('extracted_info', {})
            }
        return None

    def clear_interactive_scenario_progress(self, lesson_id: str, scenario_id: str):
        """Limpia el progreso de un escenario interactivo cuando se completa."""
        if lesson_id in self.interactive_scenario_progress and scenario_id in self.interactive_scenario_progress[lesson_id]:
            del self.interactive_scenario_progress[lesson_id][scenario_id]
            if not self.interactive_scenario_progress[lesson_id]:  # Remove lesson entry if empty
                del self.interactive_scenario_progress[lesson_id]

    def save_user_data(self, data: dict):
        """Saves extracted variables to global user data storage."""
        self.user_data.update(data)
        self.save_progress()

    def get_user_data(self, key: str = None):
        """Retrieves user data. If key is provided, returns that specific value, otherwise returns all data."""
        if key:
            return self.user_data.get(key)
        return self.user_data.copy()
