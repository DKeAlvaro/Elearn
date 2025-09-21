# views/home_view.py
import flet as ft
from app_state import AppState
import config
from billing_manager import billing_manager

def HomeView(page: ft.Page, app_state: AppState):

    def start_lesson(e):
        lesson_id = e.control.data
        # Check if lesson is unlocked using the same logic as the UI
        try:
            lesson_num = int(lesson_id[1:])  # Extract number from L01, L02, etc.
        except (ValueError, IndexError):
            lesson_num = 999  # Default to high number if parsing fails
        
        # Every 3rd lesson (3, 6, 9, etc.) requires premium, others are free
        is_premium_lesson = (lesson_num % 3 == 0)
        is_unlocked = (not is_premium_lesson) or has_premium or app_state.is_lesson_unlocked(lesson_id)
        
        if is_unlocked:
            app_state.select_lesson(lesson_id)
            page.go("/lesson")
    
    def go_to_settings(e):
        """Navigate to settings page"""
        page.go("/settings")
    
    def go_to_premium(e):
        page.go("/premium")
    
    # Check if user has premium access
    has_premium = billing_manager.check_premium_status()

    lessons = app_state.data_manager.get_lessons()
    lesson_cards = []
    
    for lesson in lessons:
        lesson_id = lesson.get("id")
        is_completed = app_state.is_lesson_completed(lesson_id)
        # Extract numeric part from lesson ID (e.g., 'L01' -> 1)
        try:
            lesson_number = int(lesson_id.replace('L', '').lstrip('0') or '0')
        except (ValueError, AttributeError):
            lesson_number = 999  # Default to locked if can't parse
        
        # Every 3rd lesson (3, 6, 9, etc.) requires premium, others are free
        is_premium_lesson = (lesson_number % 3 == 0)
        is_unlocked = (not is_premium_lesson) or has_premium or app_state.is_lesson_unlocked(lesson_id)
        
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
            button_text = "Unlock Premium"
            button_color = ft.Colors.AMBER
            button_disabled = False
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
                            on_click=start_lesson if is_unlocked else go_to_premium,
                            data=lesson_id,
                            color=button_color,
                            disabled=False,
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