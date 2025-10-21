# views/intro_view.py
import flet as ft
import src.config as config
from src.ui_components import AppLogo, Title, Subtitle, PrimaryButton

def IntroView(page: ft.Page, on_start: callable):
    
    def handle_start(e):
        on_start()

    return ft.View(
        "/intro",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        AppLogo(),
                        Title(config.get_text("welcome_title", "Welcome to ELearn")),
                        Subtitle(config.get_text("welcome_subtitle", "Your personal AI-powered language tutor")),
                        ft.Container(height=30),
                        PrimaryButton(
                            text=config.get_text("start_learning", "Start Learning"),
                            on_click=handle_start,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                ),
                expand=True,
                padding=ft.padding.all(32),
                alignment=ft.alignment.center,
            )
        ],
        padding=0,
    )