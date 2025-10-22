# app_state.py
import src.config as config
from src.managers.data_manager import DataManager
from src.managers.progress_manager import ProgressManager
from src.managers.user_data_manager import user_data_manager
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
        self.offline_mode = False
        
        # Load saved user session if available
        self._load_saved_session()

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
        
        if current_lesson_index == 0:
            return "unlocked"
        
        return "unlocked"

    def _load_saved_session(self):
        """Load saved user session on app startup"""
        try:
            if user_data_manager.has_valid_session():
                session = user_data_manager.get_user_session()
                user_data = session.get("user_data")
                if user_data:
                    # Create user object from saved session
                    class SavedUser:
                        def __init__(self, session_data):
                            self.uid = session_data.get('uid')
                            self.email = session_data.get('email')
                            self.display_name = session_data.get('name')
                            self.picture = session_data.get('picture')
                            self.provider = session_data.get('provider', 'google.com')
                            self.access_token = session_data.get('access_token')
                            self.refresh_token = session_data.get('refresh_token')
                    
                    self.user = SavedUser(user_data)
                    self.offline_mode = session.get("offline_mode", False)
                    print(f"Restored user session for: {user_data.get('name', user_data.get('email'))}")
        except Exception as e:
            print(f"Error loading saved session: {e}")
            user_data_manager.clear_user_session()

    def login_user(self, user_data, offline_mode=False):
        """Login user and save session"""
        self.user = user_data
        user_data_manager.save_user_session(user_data, offline_mode)

    def logout_user(self):
        """Logout user and clear session"""
        self.user = None
        self.offline_mode = False
        user_data_manager.clear_user_session()

    def is_user_logged_in(self):
        """Check if user is logged in"""
        return self.user is not None

    def enable_offline_mode(self):
        """Enable offline mode for current session"""
        self.offline_mode = True
        if self.user:
            # Update session with offline mode
            session = user_data_manager.get_user_session()
            if session:
                user_data_manager.save_user_session(session.get("user_data"), offline_mode=True)
