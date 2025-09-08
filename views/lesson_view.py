# views/lesson_view.py
import flet as ft
from app_state import AppState
from ui_factory import create_slide_content
# +++ NEW IMPORTS +++
from ui_components import ChatMessage, LoadingMessage 
from utils.typing_simulator import simulate_typing
from llm_client import LLMClient
import config
import json
import re
import asyncio

class LessonView(ft.View):
    def __init__(self, page: ft.Page, app_state: AppState, llm_client: LLMClient):
        super().__init__(route="/lesson")
        self.page = page
        self.app_state = app_state
        self.llm_client = llm_client
        
        self.chat_history = []
        self.required_concepts = []
        self.covered_concepts = set()

        self.slide_content_area = ft.Container(
            alignment=ft.alignment.center,
            padding=20,
            expand=True
        )

        self.previous_button = ft.ElevatedButton(config.get_text("previous"), on_click=self.go_previous, visible=False)
        self.next_button = ft.ElevatedButton(on_click=self.go_next)

        self.controls = [
            ft.AppBar(
                title=ft.Column([
                    ft.Row([
                        ft.Image(
                            src="assets/logo.svg",
                            width=24,
                            height=24,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Container(width=4),
                        ft.Container(
                            content=ft.Text(
                                self.app_state.get_current_lesson_title(),
                                text_align=ft.TextAlign.CENTER,
                                size=16,
                                weight=ft.FontWeight.W_500
                            ),
                            expand=True
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=0, tight=True),
                center_title=True
            ),
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
        self.next_button.text = config.get_text("finish", "Finalizar") if is_last_slide else config.get_text("next", "Siguiente")
        self.previous_button.visible = self.app_state.current_slide_index > 0
        
        # Disable 'Finalizar' button by default on last slide
        if is_last_slide:
            slide_type = current_slide_data.get("type")
            # Only disable for interactive scenarios and llm_check types
            if slide_type in ["interactive_scenario", "llm_check"]:
                self.next_button.disabled = True
            else:
                self.next_button.disabled = False
        else:
            self.next_button.disabled = False

        slide_elements = create_slide_content(current_slide_data)
        self.slide_content_area.content = slide_elements["container"]
        
        slide_type = current_slide_data.get("type")

        if slide_type == "interactive_scenario":
            self.handle_interactive_scenario(slide_elements, current_slide_data)
        elif slide_type == "llm_check":
            self.handle_llm_check(slide_elements, current_slide_data)
        
        self.page.update()

    # +++ FULLY REVISED METHOD with async, loading, and typing effect +++
    def handle_interactive_scenario(self, slide_elements, slide_data):
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
            progress_text.value = config.get_text("progress_text", "Progreso: {covered} / {total} conceptos cubiertos").format(covered=covered, total=total)
            
            is_completed = covered == total and total > 0
            if is_completed:
                progress_text.value = config.get_text("objective_completed", "¡Objetivo completado!")
                # Enable the Finalizar button when interactive scenario is completed
                lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
                is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
                if is_last_slide:
                    self.next_button.disabled = False
                    self.next_button.text = "Finalizar"
                # Disable inputs
                send_button.disabled = True
                new_message.disabled = True
            else:
                # Keep Finalizar button disabled if not completed
                lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
                is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
                if is_last_slide:
                    self.next_button.disabled = True
            
            # This needs to be called to update the UI elements
            self.page.update()

        concepts_to_check = {
            item_id: self.app_state.data_manager.get_content_by_item_id(item_id)
            for item_id in self.required_concepts
        }

        initial_prompt = slide_data.get("initial_prompt", "Hola.")
        chat_messages.controls.append(ChatMessage(ft.Text(initial_prompt, selectable=True), is_user=False))
        self.chat_history.append({"role": "assistant", "content": initial_prompt})
        update_progress_ui()
        
        async def send_message_click(e):
            user_input = new_message.value
            if not user_input or send_button.disabled:
                return
            
            # 1. Immediately add user message and clear input
            chat_messages.controls.append(ChatMessage(ft.Text(user_input, selectable=True), is_user=True))
            new_message.value = ""
            send_button.disabled = True
            
            # 2. Add loading indicator and update UI immediately
            loading = LoadingMessage()
            chat_messages.controls.append(loading)
            self.page.update()  # This should show user message and loading immediately

            # 3. Add to chat history
            self.chat_history.append({"role": "user", "content": user_input})

            # 4. Run LLM call in a separate task to avoid blocking
            async def get_llm_response():
                persona = slide_data.get("llm_persona", "un asistente")
                # Wrap the synchronous LLM call in an executor to make it non-blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    full_response = await loop.run_in_executor(
                        executor, 
                        self.llm_client.get_scenario_response, 
                        persona, 
                        self.chat_history, 
                        concepts_to_check
                    )
                return full_response
            
            # 5. Get the response asynchronously
            try:
                full_response = await get_llm_response()
                
                chat_response = "Hubo un error al procesar la respuesta."
                try:
                    control_line, parsed_response = full_response.split('\n', 1)
                    match = re.search(r'\[.*\]', control_line)
                    if match:
                        newly_covered_ids = json.loads(match.group(0))
                        for item_id in newly_covered_ids:
                            self.covered_concepts.add(item_id)
                    chat_response = parsed_response.strip()
                except (ValueError, json.JSONDecodeError) as err:
                    print(f"Error parsing LLM response: {err}")

                # 6. Remove loading and prepare for typing effect
                chat_messages.controls.remove(loading)
                assistant_text_control = ft.Text(selectable=True)
                chat_messages.controls.append(ChatMessage(assistant_text_control, is_user=False))
                self.page.update()

                # 7. Simulate typing the response
                await simulate_typing(assistant_text_control, chat_response, self.page)

                self.chat_history.append({"role": "assistant", "content": chat_response})
                
                # 8. Update progress and re-enable inputs if not completed
                update_progress_ui()
                if len(self.covered_concepts) < len(self.required_concepts):
                     send_button.disabled = False

                self.page.update()
                
            except Exception as e:
                # Handle any errors
                chat_messages.controls.remove(loading)
                error_text = ft.Text(f"Error: {str(e)}", selectable=True)
                chat_messages.controls.append(ChatMessage(error_text, is_user=False))
                send_button.disabled = False
                self.page.update()

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
            
            # Enable Finalizar button after getting correction (assuming completion)
            lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
            is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
            if is_last_slide:
                self.next_button.disabled = False
            
            self.page.update()

        check_button.on_click = check_answer_click

    def go_previous(self, e):
        if self.app_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        # Don't proceed if button is disabled
        if self.next_button.disabled:
            return
            
        if self.app_state.next_slide():
            self.update_slide_content()
        else:
            # Mark lesson as completed when finishing
            self.app_state.mark_lesson_completed(self.app_state.current_lesson_id)
            self.page.go('/')