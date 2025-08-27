# views/lesson_view.py

import flet as ft
from app_state import AppState
from ui_factory import create_slide_content
from llm_client import LLMClient

class LessonView(ft.View):
    def __init__(self, page: ft.Page, app_state: AppState, llm_client: LLMClient):
        super().__init__(route="/lesson")
        self.page = page
        self.app_state = app_state
        self.llm_client = llm_client

        # Contenedor que tendrá el contenido dinámico de la diapositiva
        self.slide_content_area = ft.Container(
            alignment=ft.alignment.center,
            padding=20,
            expand=True
        )

        self.previous_button = ft.ElevatedButton("Anterior", on_click=self.go_previous, visible=False)
        self.next_button = ft.ElevatedButton(on_click=self.go_next)

        self.controls = [
            ft.AppBar(title=ft.Text(self.app_state.get_current_lesson_title())),
            self.slide_content_area,
            ft.Row(
                [self.previous_button, self.next_button],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]
        
        # Cargar la primera diapositiva al construir la vista
        self.update_slide_content()

    def update_slide_content(self):
        """Obtiene los datos de la diapositiva actual y actualiza el área de contenido."""
        current_slide_data = self.app_state.get_current_slide_data()
        if not current_slide_data:
            return

        # Actualizar texto del botón
        lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
        is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
        self.next_button.text = "Finalizar" if is_last_slide else "Siguiente"

        # Mostrar/ocultar botón "Anterior"
        self.previous_button.visible = self.app_state.current_slide_index > 0

        # Generar contenido con la factory
        slide_elements = create_slide_content(current_slide_data)
        
        # Limpiar el contenido anterior
        self.slide_content_area.content = slide_elements["container"]

        # Si es una diapositiva de LLM, conectar los eventos
        if current_slide_data.get("type") == "llm_check":
            answer_field = slide_elements["answer_field"]
            check_button = slide_elements["check_button"]
            result_text = slide_elements["result_text"]
            
            # Crear una función `on_click` específica para este botón
            def check_answer_click(e):
                user_input = answer_field.value
                if not user_input:
                    return
                
                check_button.disabled = True
                result_text.value = "Pensando..."
                self.page.update()

                correction = self.llm_client.get_correction(user_input, current_slide_data["prompt"])
                
                result_text.value = correction
                check_button.disabled = False
                self.page.update()

            check_button.on_click = check_answer_click
        
        self.page.update()

    def go_previous(self, e):
        """Maneja el clic en el botón Anterior."""
        if self.app_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        """Maneja el clic en el botón Siguiente/Finalizar."""
        if self.app_state.next_slide():
            # Si hay una siguiente diapositiva, simplemente actualizamos el contenido
            self.update_slide_content()
        else:
            # Si no, volvemos a la pantalla de inicio
            self.page.go('/')