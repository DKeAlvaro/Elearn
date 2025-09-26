# settings_manager.py
import flet as ft
import config

class SettingsManager:
    def __init__(self, llm_client, page: ft.Page):
        self.llm_client = llm_client
        self.page = page

    def save_api_key(self, api_key: str, status_message: ft.Text):
        if not api_key:
            status_message.value = config.get_text("api_key_empty_error", "Please enter an API key")
            status_message.color = ft.Colors.RED
        else:
            try:
                config.save_user_api_key(api_key)
                status_message.value = config.get_text("api_key_saved", "API key saved successfully!")
                status_message.color = ft.Colors.GREEN
                
                config.update_runtime_api_key(api_key)
                
                if self.llm_client:
                    self.llm_client.update_api_key()
                
            except Exception as ex:
                status_message.value = config.get_text("api_key_save_error", "Error saving API key: {error}").format(error=str(ex))
                status_message.color = ft.Colors.RED
        
        self.page.update()

    def clear_api_key(self, api_key_field: ft.TextField, status_message: ft.Text):
        try:
            config.clear_user_api_key()
            api_key_field.value = ""
            status_message.value = config.get_text("api_key_cleared", "API key cleared successfully!")
            status_message.color = ft.Colors.ORANGE
            
            config.update_runtime_api_key(None)
            
            if self.llm_client:
                self.llm_client.update_api_key()
            
        except Exception as ex:
            status_message.value = config.get_text("api_key_clear_error", "Error clearing API key: {error}").format(error=str(ex))
            status_message.color = ft.Colors.RED
        
        self.page.update()