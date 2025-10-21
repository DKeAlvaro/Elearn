# views/home_view.py
import flet as ft
import src.config as config
from src.ui_components import CustomAppBar
from src.view_models.home_view_model import HomeViewModel
from src.app_state import AppState


def HomeView(page: ft.Page, app_state: AppState):
    view_model = HomeViewModel(app_state, page)

    lesson_cards = []
    for item in view_model.get_lesson_items():
        lesson_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        item.status_indicator,
                        ft.Text(
                            item.title,
                            size=16,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                            color=item.text_color
                        )
                    ], alignment=ft.MainAxisAlignment.START, spacing=12),
                    ft.Container(
                        content=ft.TextButton(
                            text=item.button_text,
                            on_click=item.button_click,
                            data=item.lesson_id,
                            disabled=item.button_disabled,
                            style=ft.ButtonStyle(
                                color=item.button_color,
                                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_500),
                                padding=ft.padding.symmetric(horizontal=16, vertical=8)
                            )
                        ),
                        alignment=ft.alignment.center_right
                    )
                ], spacing=12),
                padding=16,
                border_radius=8,
                bgcolor=item.card_bgcolor,
                border=item.card_border
            ),
            elevation=item.card_elevation,
            margin=ft.margin.symmetric(vertical=4)
        )
        lesson_cards.append(lesson_card)

    return ft.View(
        "/",
        controls=[
            CustomAppBar(
                title=config.get_text("choose_lesson", "Choose a lesson"),
                page=page,
                actions=[
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip=config.get_text("settings", "Settings"),
                        on_click=view_model.go_to_settings
                    )
                ]
            ),
            ft.Container(
                content=ft.Column(
                    controls=lesson_cards,
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
