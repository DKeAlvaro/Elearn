# main.py

import flet as ft
import config
from data_manager import DataManager
from app_state import AppState
from llm_client import LLMClient
from views.home_view import HomeView
from views.lesson_view import LessonView
from views.settings_view import SettingsView

def main(page: ft.Page):
    page.title = config.get_text("app_title", "Language Learning App")
    
    # Set app icon using the logo
    page.window_icon = "assets/logo.svg"
    
    # Set web app icon (favicon) for browser
    page.web_app_icon = "assets/logo.svg"
    
    # Mobile-optimized page settings
    page.window_width = 400
    page.window_height = 800
    page.window_min_width = 350
    page.window_min_height = 600
    page.adaptive = True
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = ft.padding.symmetric(horizontal=16, vertical=8)
    
    # Show loading screen initially
    loading_screen = ft.Column([
        ft.Container(height=80),  # Add top spacing to lower the logo
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
    alignment=ft.MainAxisAlignment.CENTER)
    
    page.add(loading_screen)
    page.update()
    
    # Modern typography with responsive scaling
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
    }
    
    # Simulate loading time
    import time
    time.sleep(2)
    
    # Remove loading screen
    page.clean()
    
    # --- Inicialización ---
    # DataManager now automatically uses the current language configuration
    data_manager = DataManager()
    app_state = AppState(data_manager)
    llm_client = LLMClient()

    # --- Enrutamiento ---
    def route_change(route):
        page.views.clear()
        page.views.append(HomeView(page, app_state))

        if page.route == "/lesson":
            page.views.append(LessonView(page, app_state, llm_client))
        elif page.route == "/settings":
            page.views.append(SettingsView(page, llm_client))
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)#, view=ft.AppView.WEB_BROWSER)