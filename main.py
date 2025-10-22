# main.py

import flet as ft
import src.config as config
from src.data_manager import DataManager
from src.app_state import AppState
from src.llm_client import LLMClient
from src.views.home_view import HomeView
from src.views.lesson_view import LessonView
from src.views.settings_view import SettingsView
from src.views.premium_view import PremiumView
from src.views.intro_view import IntroView
from src.views.login_view import LoginView
from src.billing_manager import billing_manager
from src.settings_manager import SettingsManager

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

def main(page: ft.Page):
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
    
    # --- Inicialización ---
    data_manager = DataManager()
    app_state = AppState(data_manager)
    llm_client = LLMClient()
    settings_manager = SettingsManager(llm_client, page)
    
    # Check premium status and update app_state
    has_premium = billing_manager.check_premium_status()
    app_state.update_premium_status(has_premium)
    
    # Add a small delay to ensure loading screen is visible
    import time
    time.sleep(1)
    
    # Remove loading screen after initialization
    page.clean()

    def on_start_learning():
        data_manager.set_first_run_completed()
        page.go("/")

    # --- Enrutamiento ---
    def route_change(route):
        page.views.clear()

        if not app_state.user and page.route not in ["/login", "/intro"]:
            page.go("/login")
            return

        if page.route == "/login":
            page.views.append(LoginView(page, app_state))
        elif page.route == "/intro":
            page.views.append(IntroView(page, on_start_learning))
        else:
            page.views.append(HomeView(page, app_state))
            if page.route == "/lesson":
                page.views.append(LessonView(page, app_state, llm_client))
            elif page.route == "/settings":
                page.views.append(SettingsView(page, settings_manager))
            elif page.route == "/premium":
                page.views.append(PremiumView(page))
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if data_manager.is_first_run():
        page.go("/intro")
    elif not app_state.user:
        page.go("/login")
    else:
        page.go("/")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")