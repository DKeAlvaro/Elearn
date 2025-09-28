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
        self.interactive_scenario_progress = {}  # Track interactive scenario progress
        self.lesson_slide_positions = {}  # Track current slide position for each lesson
        self.user_data = {}  # Global user data storage for extracted variables
        self.progress_file = "progress.json"  # File to persist progress
        self.has_premium = False
        
        # Scenario-related attributes
        self.scenario_user_goals = []
        self.scenario_completed_goals = set()
        self.scenario_current_goal_index = 0
        self.scenario_extracted_info = {}
        self.scenario_chat_history = []
        
        self.load_progress()

    def update_premium_status(self, has_premium: bool):
        self.has_premium = has_premium

    def select_lesson(self, lesson_id: str):
        """Selecciona una lección para empezar."""
        self.current_lesson_id = lesson_id
        # Restore saved slide position or start at 0 if no saved position
        self.current_slide_index = self.lesson_slide_positions.get(lesson_id, 0)

    def next_slide(self):
        """Avanza a la siguiente diapositiva. Devuelve True si es posible, False si la lección ha terminado."""
        content = self.data_manager.get_lesson_content(self.current_lesson_id)
        if self.current_slide_index < len(content) - 1:
            self.current_slide_index += 1
            # Save the new slide position
            self.lesson_slide_positions[self.current_lesson_id] = self.current_slide_index
            self.save_progress()
            return True
        return False

    def previous_slide(self):
        """Retrocede a la diapositiva anterior. Devuelve True si es posible, False si ya está en la primera."""
        if self.current_slide_index > 0:
            self.current_slide_index -= 1
            # Save the new slide position
            self.lesson_slide_positions[self.current_lesson_id] = self.current_slide_index
            self.save_progress()
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
    
    def reset_scenario_state(self):
        """Resets the current scenario state to initial values."""
        # Save any extracted variables to global storage before clearing
        if self.scenario_extracted_info:
            self.save_user_data(self.scenario_extracted_info)
        
        self.scenario_completed_goals = set()
        self.scenario_current_goal_index = 0
        self.scenario_extracted_info = {}
        self.scenario_chat_history = []
    
    def save_user_data(self, data: dict):
        """Saves extracted variables to global user data storage."""
        self.user_data.update(data)
        self.save_progress()
    
    def get_user_data(self, key: str = None):
        """Retrieves user data. If key is provided, returns that specific value, otherwise returns all data."""
        if key:
            return self.user_data.get(key)
        return self.user_data.copy()
    
    def get_all_available_variables(self):
        """Returns all available variables from both global user data and current scenario."""
        all_vars = self.user_data.copy()
        all_vars.update(self.scenario_extracted_info)
        return all_vars
    
    def is_lesson_unlocked(self, lesson_id: str, has_premium: bool) -> bool:
        """Verifica si una lección está desbloqueada, considerando el estado premium."""
        lessons = self.data_manager.get_lessons()
        
        # Find the current lesson index
        current_lesson_index = -1
        for i, lesson in enumerate(lessons):
            if lesson.get("id") == lesson_id:
                current_lesson_index = i
                break
        
        if current_lesson_index == -1:
            return False  # Lesson not found
        
        # First lesson is always unlocked
        if current_lesson_index == 0:
            return True
        
        # For free users: every 4th lesson is locked (lessons 4, 8, 12, etc.)
        # This means lesson numbers 4, 8, 12... (indices 3, 7, 11...) are premium-only
        lesson_number = current_lesson_index + 1  # Convert 0-based index to 1-based lesson number
        if not has_premium and lesson_number % 4 == 0:
            return False  # Premium required for every 4th lesson
        
        # Check progression: find the most recent completed lesson that's accessible to this user
        for i in range(current_lesson_index - 1, -1, -1):
            previous_lesson = lessons[i]
            previous_lesson_number = i + 1
            previous_lesson_id = previous_lesson.get("id")
            
            # If this previous lesson is premium-locked for free users, skip it
            if not has_premium and previous_lesson_number % 4 == 0:
                continue
            
            # Check if this accessible previous lesson is completed
            return self.is_lesson_completed(previous_lesson_id)
        
        # If no accessible previous lesson found, this means we're at lesson 1 or 2
        return True
    
    def get_lesson_lock_reason(self, lesson_id: str, has_premium: bool) -> str:
        """Returns the reason why a lesson is locked: 'unlocked', 'premium', or 'progression'."""
        lessons = self.data_manager.get_lessons()
        
        # Find the current lesson index
        current_lesson_index = -1
        for i, lesson in enumerate(lessons):
            if lesson.get("id") == lesson_id:
                current_lesson_index = i
                break
        
        if current_lesson_index == -1:
            return "progression"  # Lesson not found, treat as progression lock
        
        # First lesson is always unlocked
        if current_lesson_index == 0:
            return "unlocked"
        
        # Check if this is a premium-only lesson for free users
        lesson_number = current_lesson_index + 1  # Convert 0-based index to 1-based lesson number
        if not has_premium and lesson_number % 4 == 0:
            return "premium"  # Premium required for every 4th lesson
        
        # Check progression: find the most recent completed lesson that's accessible to this user
        for i in range(current_lesson_index - 1, -1, -1):
            previous_lesson = lessons[i]
            previous_lesson_number = i + 1
            previous_lesson_id = previous_lesson.get("id")
            
            # If this previous lesson is premium-locked for free users, skip it
            if not has_premium and previous_lesson_number % 4 == 0:
                continue
            
            # Check if this accessible previous lesson is completed
            if self.is_lesson_completed(previous_lesson_id):
                return "unlocked"
            else:
                return "progression"  # Previous lesson not completed
        
        # If no accessible previous lesson found, this means we're at lesson 1 or 2
        return "unlocked"
    
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