# views/home_view.py
import flet as ft
from app_state import AppState
import config

def HomeView(page: ft.Page, app_state: AppState):

    def start_lesson(e):
        lesson_id = e.control.data
        # Solo permitir iniciar lecciones desbloqueadas
        if app_state.is_lesson_unlocked(lesson_id):
            app_state.select_lesson(lesson_id)
            page.go("/lesson")
    
    def go_to_settings(e):
        """Navigate to settings page"""
        page.go("/settings")

    lessons = app_state.data_manager.get_lessons()
    lesson_cards = []
    
    for lesson in lessons:
        lesson_id = lesson.get("id")
        is_completed = app_state.is_lesson_completed(lesson_id)
        is_unlocked = app_state.is_lesson_unlocked(lesson_id)
        
        # Create status indicator (completed, unlocked, or locked)
        if is_completed:
            status_indicator = ft.Icon(
                ft.Icons.CHECK_CIRCLE,
                color=ft.Colors.GREEN,
                size=24
            )
        elif is_unlocked:
            status_indicator = ft.Icon(
                ft.Icons.RADIO_BUTTON_UNCHECKED,
                color=ft.Colors.GREY_400,
                size=24
            )
        else:
            status_indicator = ft.Icon(
                ft.Icons.LOCK,
                color=ft.Colors.GREY_600,
                size=24
            )
        
        # Update button text and properties based on lesson status
        if not is_unlocked:
            button_text = config.get_text("locked", "Bloqueado")
            button_color = ft.Colors.GREY_400
            button_disabled = True
        elif is_completed:
            button_text = config.get_text("review_lesson", "Repasar")
            button_color = ft.Colors.BLUE_GREY
            button_disabled = False
        else:
            button_text = config.get_text("start_lesson", "Comenzar")
            button_color = None
            button_disabled = False
        
        # Modern card-based design for lessons with locked state styling
        lesson_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        status_indicator,
                        ft.Text(
                            lesson.get("title"),
                            size=18,
                            weight=ft.FontWeight.W_600,
                            expand=True,
                            color=ft.Colors.GREY_500 if not is_unlocked else None
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text=button_text,
                            on_click=start_lesson if is_unlocked else None,
                            data=lesson_id,
                            color=button_color,
                            disabled=button_disabled,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(horizontal=24, vertical=12)
                            )
                        ),
                        alignment=ft.alignment.center_right
                    )
                ], spacing=16),
                padding=20,
                border_radius=16,
                opacity=0.6 if not is_unlocked else 1.0,
                bgcolor=ft.Colors.GREY_100 if not is_unlocked else None
            ),
            elevation=1 if not is_unlocked else 2,
            margin=ft.margin.symmetric(vertical=8)
        )
        lesson_cards.append(lesson_card)

    return ft.View(
        "/",
        controls=[
            ft.AppBar(
                title=ft.Row([
                    ft.Image(
                        src="assets/logo.svg",
                        width=32,
                        height=32,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Container(width=12),
                    ft.Text(
                        config.get_text("choose_lesson", "Elige una lección"),
                        size=20,
                        weight=ft.FontWeight.W_600
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                center_title=True,
                bgcolor=ft.Colors.TRANSPARENT,
                elevation=0,
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip=config.get_text("settings", "Settings"),
                        on_click=go_to_settings
                    )
                ]
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        *lesson_cards
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    spacing=0
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                expand=True
            )
        ],
        padding=0,
        scroll=ft.ScrollMode.AUTO
    )