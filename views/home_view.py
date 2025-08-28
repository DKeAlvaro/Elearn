# views/home_view.py
import flet as ft
from app_state import AppState
import config

def HomeView(page: ft.Page, app_state: AppState):

    def start_lesson(e):
        lesson_id = e.control.data
        app_state.select_lesson(lesson_id)
        page.go("/lesson")

    lessons = app_state.data_manager.get_lessons()
    lesson_cards = []
    
    for lesson in lessons:
        lesson_id = lesson.get("id")
        is_completed = app_state.is_lesson_completed(lesson_id)
        
        # Create completion indicator
        completion_indicator = ft.Icon(
            ft.Icons.CHECK_CIRCLE,
            color=ft.Colors.GREEN,
            size=24
        ) if is_completed else ft.Icon(
            ft.Icons.RADIO_BUTTON_UNCHECKED,
            color=ft.Colors.GREY_400,
            size=24
        )
        
        # Update button text based on completion status
        button_text = config.get_text("review_lesson", "Repasar") if app_state.is_lesson_completed(lesson_id) else config.get_text("start_lesson", "Comenzar")
        button_color = ft.Colors.BLUE_GREY if is_completed else None
        
        # Modern card-based design for lessons
        lesson_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        completion_indicator,
                        ft.Text(
                            lesson.get("title"),
                            size=18,
                            weight=ft.FontWeight.W_600,
                            expand=True
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text=button_text,
                            on_click=start_lesson,
                            data=lesson_id,
                            color=button_color,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                padding=ft.padding.symmetric(horizontal=24, vertical=12)
                            )
                        ),
                        alignment=ft.alignment.center_right
                    )
                ], spacing=16),
                padding=20,
                border_radius=16
            ),
            elevation=2,
            margin=ft.margin.symmetric(vertical=8)
        )
        lesson_cards.append(lesson_card)

    return ft.View(
        "/",
        controls=[
            ft.AppBar(
                title=ft.Text(
                    config.get_text("choose_lesson", "Elige una lección"),
                    size=20,
                    weight=ft.FontWeight.W_600
                ),
                center_title=True,
                bgcolor=ft.Colors.TRANSPARENT,
                elevation=0
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