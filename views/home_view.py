import flet as ft
from app_state import AppState
3
def HomeView(page: ft.Page, app_state: AppState):

    def start_lesson(e):
        lesson_id = e.control.data
        app_state.select_lesson(lesson_id)
        page.go("/lesson")

    lessons = app_state.data_manager.get_lessons()
    lesson_cards = []
    
    for lesson in lessons:
        # Modern card-based design for lessons
        lesson_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            lesson.get("title"),
                            size=18,
                            weight=ft.FontWeight.W_600,
                            expand=True
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="Comenzar",
                            on_click=start_lesson,
                            data=lesson.get("id"),
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
                    "Elige una lección",
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