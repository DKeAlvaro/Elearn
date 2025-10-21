# views/lesson_view.py
import flet as ft
import src.config as config
from src.app_state import AppState
from src.llm_client import LLMClient
from src.ui_components import CustomAppBar
from src.view_models.lesson_view_model import LessonViewModel

class LessonView(ft.View):
    def __init__(self, page: ft.Page, app_state: AppState, llm_client: LLMClient):
        super().__init__(route="/lesson")
        self.page = page
        self.app_state = app_state
        self.llm_client = llm_client

        self.slide_content_area = ft.Container(
            alignment=ft.alignment.center,
            padding=ft.padding.only(left=20, right=20, top=20, bottom=5),
            expand=True
        )

        self.previous_button = ft.ElevatedButton(
            "Anterior", 
            on_click=self.go_previous, 
            visible=True,
            disabled=True,
            opacity=0.0
        )
        self.next_button = ft.ElevatedButton(text="Siguiente", on_click=self.go_next)

        self.view_model = LessonViewModel(app_state, llm_client, page, self)

        self.controls = [
            CustomAppBar(
                title=self.app_state.lesson_state.get_current_lesson_title(),
                page=page,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self.go_back_to_home
                )
            ),
            self.slide_content_area,
            ft.Container(
                content=ft.Row(
                    [self.previous_button, self.next_button],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=ft.padding.only(bottom=10, left=16, right=16, top=0),
                height=50
            )
        ]
        
        self.view_model.update_slide_content()

    def go_back_to_home(self, e):
        self.view_model.go_back_to_home(e)

    def go_previous(self, e):
        self.view_model.go_previous(e)

    def go_next(self, e):
        self.view_model.go_next(e)
