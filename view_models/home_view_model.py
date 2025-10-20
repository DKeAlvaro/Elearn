# view_models/home_view_model.py
import flet as ft
from app_state import AppState
import config
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass
class LessonItemViewModel:
    lesson_id: str
    title: str
    status_indicator: ft.Icon
    button_text: str
    button_color: str
    button_click: Optional[Callable]
    button_disabled: bool
    card_bgcolor: Optional[str]
    card_border: Optional[ft.Border]
    text_color: Optional[str]
    card_elevation: int

class HomeViewModel:
    def __init__(self, app_state: AppState, page: ft.Page):
        self.app_state = app_state
        self.page = page

    def get_lesson_items(self) -> list[LessonItemViewModel]:
        lessons = self.app_state.data_manager.get_lessons()
        lesson_items = []

        for lesson in lessons:
            lesson_id = lesson.get("id")
            is_completed = self.app_state.progress_manager.is_lesson_completed(lesson_id)
            lock_reason = self.app_state.get_lesson_lock_reason(lesson_id)

            status_indicator, button_text, button_color, button_click, button_disabled = self._get_button_and_status(lock_reason, is_completed, lesson_id)
            card_bgcolor, card_border, text_color, card_elevation = self._get_card_style(lock_reason)

            lesson_items.append(
                LessonItemViewModel(
                    lesson_id=lesson_id,
                    title=lesson.get("title"),
                    status_indicator=status_indicator,
                    button_text=button_text,
                    button_color=button_color,
                    button_click=button_click,
                    button_disabled=button_disabled,
                    card_bgcolor=card_bgcolor,
                    card_border=card_border,
                    text_color=text_color,
                    card_elevation=card_elevation,
                )
            )
        return lesson_items

    def _get_button_and_status(self, lock_reason, is_completed, lesson_id):
        if is_completed:
            status_indicator = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20)
            button_text = config.get_text("review_lesson", "Review")
            button_color = ft.Colors.BLUE_GREY_400
            button_click = self._start_lesson
            button_disabled = False
        elif lock_reason == "unlocked":
            status_indicator = ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, color=ft.Colors.BLUE, size=20)
            button_text = config.get_text("start_lesson", "Start")
            button_color = ft.Colors.BLUE
            button_click = self._start_lesson
            button_disabled = False
        elif lock_reason == "premium":
            status_indicator = ft.Icon(ft.Icons.STAR_BORDER, color=ft.Colors.ORANGE_300, size=20)
            button_text = "Premium"
            button_color = ft.Colors.ORANGE_300
            button_click = self._go_to_premium
            button_disabled = False
        else:  # progression lock
            status_indicator = ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.GREY_400, size=20)
            button_text = "Locked"
            button_color = ft.Colors.GREY_400
            button_click = None
            button_disabled = True
        
        return status_indicator, button_text, button_color, button_click, button_disabled

    def _get_card_style(self, lock_reason):
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
        return card_bgcolor, card_border, text_color, card_elevation

    def _start_lesson(self, e):
        lesson_id = e.control.data
        if self.app_state.is_lesson_unlocked(lesson_id):
            self.app_state.lesson_state.select_lesson(lesson_id)
            self.page.go("/lesson")

    def _go_to_premium(self, e):
        self.page.go("/premium")

    def go_to_settings(self, e):
        self.page.go("/settings")
