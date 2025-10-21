# state/scenario_state.py

class ScenarioState:
    def __init__(self):
        self.scenario_user_goals = []
        self.scenario_completed_goals = set()
        self.scenario_current_goal_index = 0
        self.scenario_extracted_info = {}
        self.scenario_chat_history = []

    def reset(self, user_data_handler=None):
        """Resets the current scenario state to initial values."""
        # Save any extracted variables to global storage before clearing
        if self.scenario_extracted_info and user_data_handler:
            user_data_handler(self.scenario_extracted_info)
        
        self.scenario_completed_goals = set()
        self.scenario_current_goal_index = 0
        self.scenario_extracted_info = {}
        self.scenario_chat_history = []

    def get_all_available_variables(self, global_user_data):
        """Returns all available variables from both global user data and current scenario."""
        all_vars = global_user_data.copy()
        all_vars.update(self.scenario_extracted_info)
        return all_vars
