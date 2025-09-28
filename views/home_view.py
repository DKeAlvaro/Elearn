# views/home_view.py
import flet as ft
from app_state import AppState
import config
from billing_manager import billing_manager

from ui_components import CustomAppBar


def HomeView(page: ft.Page, app_state: AppState):

    def start_lesson(e):
        lesson_id = e.control.data
        if app_state.is_lesson_unlocked(lesson_id, app_state.has_premium):
            app_state.select_lesson(lesson_id)
            page.go("/lesson")
    
    def go_to_settings(e):
        page.go("/settings")
    
    def go_to_premium(e):
        page.go("/premium")

    lessons = app_state.data_manager.get_lessons()
    lesson_cards = []
    
    for lesson in lessons:
        lesson_id = lesson.get("id")
        is_completed = app_state.is_lesson_completed(lesson_id)
        lock_reason = app_state.get_lesson_lock_reason(lesson_id, app_state.has_premium)
        
        if is_completed:
            status_indicator = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20)
        elif lock_reason == "unlocked":
            status_indicator = ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, color=ft.Colors.BLUE, size=20)
        elif lock_reason == "premium":
            status_indicator = ft.Icon(ft.Icons.STAR_BORDER, color=ft.Colors.ORANGE_300, size=20)
        else:  # progression lock
            status_indicator = ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.GREY_400, size=20)
        
        if lock_reason == "premium":
            button_text = "Premium"
            button_color = ft.Colors.ORANGE_300
        elif lock_reason == "progression":
            button_text = "Locked"
            button_color = ft.Colors.GREY_400
        elif is_completed:
            button_text = config.get_text("review_lesson", "Review")
            button_color = ft.Colors.BLUE_GREY_400
        else:
            button_text = config.get_text("start_lesson", "Start")
            button_color = ft.Colors.BLUE
        
        # Determine click behavior based on lock reason
        if lock_reason == "unlocked" or is_completed:
            button_click = start_lesson
            button_disabled = False
        elif lock_reason == "premium":
            button_click = go_to_premium
            button_disabled = False
        else:  # progression lock
            button_click = None
            button_disabled = True
        
        # Determine card styling based on lock status
        if lock_reason == "premium":
            card_bgcolor = ft.Colors.with_opacity(0.02, ft.Colors.ORANGE)
            card_border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_300))
            text_color = ft.Colors.GREY_600
            card_elevation = 0
        elif lock_reason == "progression":
            card_bgcolor = ft.Colors.with_opacity(0.01, ft.Colors.GREY)
            card_border = ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.GREY_400))
            text_color = ft.Colors.GREY_500
            card_elevation = 0
        else:
            card_bgcolor = None
            card_border = None
            text_color = None
            card_elevation = 1
        
        lesson_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        status_indicator,
                        ft.Text(
                            lesson.get("title"),
                            size=16,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                            color=text_color
                        )
                    ], alignment=ft.MainAxisAlignment.START, spacing=12),
                    ft.Container(
                        content=ft.TextButton(
                            text=button_text,
                            on_click=button_click,
                            data=lesson_id,
                            disabled=button_disabled,
                            style=ft.ButtonStyle(
                                color=button_color,
                                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_500),
                                padding=ft.padding.symmetric(horizontal=16, vertical=8)
                            )
                        ),
                        alignment=ft.alignment.center_right
                    )
                ], spacing=12),
                padding=16,
                border_radius=8,
                bgcolor=card_bgcolor,
                border=card_border
            ),
            elevation=card_elevation,
            margin=ft.margin.symmetric(vertical=4)
        )
        lesson_cards.append(lesson_card)

    return ft.View(
        "/",
        controls=[
            CustomAppBar(
                title=config.get_text("choose_lesson", "Elige una lección"),
                page=page,
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