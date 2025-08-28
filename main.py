# main.py

import flet as ft
import config
from data_manager import DataManager
from app_state import AppState
from llm_client import LLMClient
from views.home_view import HomeView
from views.lesson_view import LessonView

def main(page: ft.Page):
    page.title = config.get_text("app_title", "Language Learning App")
    
    # Mobile-optimized page settings
    page.window_width = 400
    page.window_height = 800
    page.window_min_width = 350
    page.window_min_height = 600
    page.adaptive = True
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.padding = ft.padding.symmetric(horizontal=16, vertical=8)
    
    # Modern typography with responsive scaling
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
    }
    
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