import flet as ft
import src.config as config
import asyncio
from src.managers.data_manager import DataManager
from src.app_state import AppState
from src.llm_client import LLMClient
from src.views.home_view import HomeView
from src.views.lesson_view import LessonView
from src.views.settings_view import SettingsView
from src.views.language_selection_view import LanguageSelectionView
from src.managers.user_data_manager import user_data_manager

from src.managers.settings_manager import SettingsManager
from src.utils.network_utils import should_enable_offline_mode

def create_loading_screen():
    return ft.Container(
        content=ft.Column([
            ft.Image(
                src="assets/logo.svg",
                width=120,
                height=120,
                fit=ft.ImageFit.CONTAIN
            ),
            ft.Container(height=30),
            ft.ProgressRing(width=40, height=40, stroke_width=4)
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.only(top=100),
        expand=True
    )

async def main(page: ft.Page):
    page.title = config.get_text("app_title", "Language Learning App")
    
    page.window_icon = "assets/logo.svg"
    page.web_app_icon = "assets/logo.svg"
    
    page.window_width = 400
    page.window_height = 800
    page.window_min_width = 350
    page.window_min_height = 600
    page.adaptive = True
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = ft.padding.only(left=16, right=16, top=8, bottom=0)
    
    loading_screen = create_loading_screen()
    page.add(loading_screen)
    page.update()
    
    # Modern typography with responsive scaling
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
    }
    
    # --- Initialization ---
    llm_client = LLMClient()
    settings_manager = SettingsManager(llm_client, page)
    
    data_manager = None
    app_state = None

    def initialize_app_state_and_managers():
        nonlocal app_state, data_manager
        data_manager = DataManager()
        app_state = AppState(data_manager)

    # Check network connectivity and enable offline mode if needed
    if should_enable_offline_mode():
        print("Network connectivity issues detected. Enabling offline mode.")
    
    # Add a small delay to ensure loading screen is visible
    await asyncio.sleep(1)
    
    # Remove loading screen after initialization
    page.clean()

    def on_language_selection_complete():
        initialize_app_state_and_managers()
        user_data_manager.set_app_data("first_run", False)
        page.go("/")

    # --- Routing ---
    def route_change(route):
        page.views.clear()

        if page.route == "/language_selection":
            page.views.append(LanguageSelectionView(page, on_language_selection_complete))
            page.update()
            return

        # This should only happen on subsequent runs
        if not app_state:
            initialize_app_state_and_managers()

        # Base view for the main app
        page.views.append(HomeView(page, app_state, llm_client))

        # Add other views on top based on the route
        route_map = {
            "/lesson": LessonView(page, app_state, llm_client),
            "/settings": SettingsView(page, settings_manager, app_state),
        }

        if page.route in route_map:
            page.views.append(route_map[page.route])

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if user_data_manager.get_app_data("first_run", True):
        page.go("/language_selection")
    else:
        initialize_app_state_and_managers()
        page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")