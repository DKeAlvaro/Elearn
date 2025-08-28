# views/lesson_view.py
import flet as ft
from app_state import AppState
from ui_factory import create_slide_content, ChatMessage
from llm_client import LLMClient
import json
import re

class LessonView(ft.View):
    def __init__(self, page: ft.Page, app_state: AppState, llm_client: LLMClient):
        super().__init__(route="/lesson")
        self.page = page
        self.app_state = app_state
        self.llm_client = llm_client
        
        # --- Estado específico del escenario ---
        self.chat_history = []
        self.required_concepts = []
        self.covered_concepts = set()

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
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        ]
        
        self.update_slide_content()

    def update_slide_content(self):
        current_slide_data = self.app_state.get_current_slide_data()
        if not current_slide_data:
            return

        lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
        is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
        self.next_button.text = "Finalizar" if is_last_slide else "Siguiente"
        self.previous_button.visible = self.app_state.current_slide_index > 0

        slide_elements = create_slide_content(current_slide_data)
        self.slide_content_area.content = slide_elements["container"]
        
        slide_type = current_slide_data.get("type")

        if slide_type == "interactive_scenario":
            self.handle_interactive_scenario(slide_elements, current_slide_data)
        elif slide_type == "llm_check":
            self.handle_llm_check(slide_elements, current_slide_data)
        
        self.page.update()

    # +++ HEAVILY MODIFIED METHOD +++
    def handle_interactive_scenario(self, slide_elements, slide_data):
        # Reiniciar estado para el nuevo escenario
        self.chat_history = []
        self.required_concepts = slide_data.get("required_concepts", [])
        self.covered_concepts = set()
        
        chat_messages = slide_elements["chat_messages"]
        new_message = slide_elements["new_message"]
        send_button = slide_elements["send_button"]
        progress_text = slide_elements["progress_text"]

        def update_progress_ui():
            total = len(self.required_concepts)
            covered = len(self.covered_concepts)
            progress_text.value = f"Progreso: {covered} / {total} conceptos cubiertos"
            if covered == total and total > 0:
                progress_text.value = "¡Objetivo completado!"
                self.next_button.text = "Lección Completada"
            self.page.update()

        # Resolver los IDs de los conceptos a su texto
        concepts_to_check = {
            item_id: self.app_state.data_manager.get_content_by_item_id(item_id)
            for item_id in self.required_concepts
        }

        # Estado inicial
        initial_prompt = slide_data.get("initial_prompt", "Hola.")
        chat_messages.controls.append(ChatMessage(initial_prompt, is_user=False))
        self.chat_history.append({"role": "assistant", "content": initial_prompt})
        update_progress_ui()
        
        def send_message_click(e):
            user_input = new_message.value
            if not user_input:
                return
            
            chat_messages.controls.append(ChatMessage(user_input, is_user=True))
            self.chat_history.append({"role": "user", "content": user_input})
            new_message.value = ""
            send_button.disabled = True
            update_progress_ui() # Actualiza UI antes de la llamada

            # Llamar al nuevo método del LLM con el contexto de los conceptos
            persona = slide_data.get("llm_persona", "un asistente")
            full_response = self.llm_client.get_scenario_response(persona, self.chat_history, concepts_to_check)
            
            # --- PARSE THE STRUCTURED RESPONSE ---
            try:
                # Separar la línea de control de la respuesta de chat
                control_line, chat_response = full_response.split('\n', 1)
                
                # Extraer la lista JSON de la línea de control
                match = re.search(r'\[.*\]', control_line)
                if match:
                    newly_covered_ids = json.loads(match.group(0))
                    for item_id in newly_covered_ids:
                        self.covered_concepts.add(item_id)
            except (ValueError, json.JSONDecodeError) as err:
                print(f"Error parsing LLM response: {err}")
                chat_response = "Hubo un error al procesar la respuesta. Inténtalo de nuevo."

            chat_messages.controls.append(ChatMessage(chat_response, is_user=False))
            self.chat_history.append({"role": "assistant", "content": chat_response})
            send_button.disabled = False
            update_progress_ui() # Actualiza UI con los nuevos conceptos cubiertos

        send_button.on_click = send_message_click
        new_message.on_submit = send_message_click

    def handle_llm_check(self, slide_elements, slide_data):
        answer_field = slide_elements["answer_field"]
        check_button = slide_elements["check_button"]
        result_text = slide_elements["result_text"]
        
        def check_answer_click(e):
            user_input = answer_field.value
            if not user_input:
                return
            
            check_button.disabled = True
            result_text.value = "Pensando..."
            self.page.update()

            correction = self.llm_client.get_correction(user_input, slide_data["prompt"])
            
            result_text.value = correction
            check_button.disabled = False
            self.page.update()

        check_button.on_click = check_answer_click

    def go_previous(self, e):
        if self.app_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        if self.app_state.next_slide():
            self.update_slide_content()
        else:
            self.page.go('/')