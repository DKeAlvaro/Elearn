import flet as ft
from src.view_models.language_selection_view_model import LanguageSelectionViewModel

class LanguageSelectionView(ft.View):
    def __init__(self, page: ft.Page, on_complete):
        super().__init__()
        self.page = page
        self.route = "/language_selection"
        self.view_model = LanguageSelectionViewModel(on_complete)

        self.target_lang_dropdown = ft.Dropdown(
            label="Select language to learn",
            options=[],
            width=300
        )
        self.download_button = ft.ElevatedButton(
            text="Download Lessons",
            on_click=self.on_download,
            disabled=True
        )
        self.progress_ring = ft.ProgressRing(width=30, height=30, stroke_width=3, visible=False)

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Welcome!", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text("Let's set up your language learning journey.", size=16),
                        ft.Container(height=30),
                        self.target_lang_dropdown,
                        ft.Container(height=20),
                        ft.Row(
                            [
                                self.download_button,
                                self.progress_ring,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        ]

        self.target_lang_dropdown.on_change = self.check_dropdowns

        self.populate_dropdowns()

    def populate_dropdowns(self):
        _, target_langs = self.view_model.get_available_languages()
        self.target_lang_dropdown.options = [ft.dropdown.Option(lang) for lang in target_langs]
        self.page.update()

    def check_dropdowns(self, e):
        if self.target_lang_dropdown.value:
            self.download_button.disabled = False
        else:
            self.download_button.disabled = True
        self.page.update()

    def on_download(self, e):
        self.download_button.disabled = True
        self.progress_ring.visible = True
        self.page.update()

        self.view_model.download_languages(
            "en",
            self.target_lang_dropdown.value
        )
