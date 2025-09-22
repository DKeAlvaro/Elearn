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
        self.extracted_info = {}  # Store extracted information for template substitution

        self.slide_content_area = ft.Container(
            alignment=ft.alignment.center,
            padding=20,
            expand=True
        )

        self.previous_button = ft.ElevatedButton(config.get_text("previous"), on_click=self.go_previous, visible=False)
        self.next_button = ft.ElevatedButton(on_click=self.go_next)

        self.controls = [
            ft.AppBar(
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self.go_back_to_home
                ),
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

    # +++ GOAL-BASED INTERACTIVE SCENARIO HANDLER +++
    def handle_interactive_scenario(self, slide_elements, slide_data):
        self.chat_history = []
        
        # Get scenario ID for progress tracking
        scenario_id = slide_data.get("scenario_id", "")
        lesson_id = self.app_state.current_lesson_id
        
        # Initialize goal-based tracking
        self.user_goals = slide_data.get("user_goal", [])
        
        # Load saved progress if available
        saved_progress = self.app_state.get_interactive_scenario_progress(lesson_id, scenario_id)
        if saved_progress:
            self.completed_goals = saved_progress['completed_goals']
            self.current_goal_index = saved_progress['current_goal_index']
            self.extracted_info = saved_progress['extracted_info']
        else:
            self.current_goal_index = 0
            self.completed_goals = set()
            self.extracted_info = {}  # Reset extracted information for new scenario
        
        scrollable_content = slide_elements["scrollable_content"]
        new_message = slide_elements["new_message"]
        send_button = slide_elements["send_button"]
        restart_button = slide_elements["restart_button"]
        progress_container = slide_elements["progress_container"]

        def update_progress_ui():
            total_goals = len(self.user_goals)
            completed_count = len(self.completed_goals)
            
            # Clear existing progress controls and rebuild with styled components
            progress_container.controls.clear()
            
            # Add objectives header
            progress_container.controls.append(
                ft.Text(
                    "Objectives:",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_700
                )
            )
            
            # Build styled progress items showing completed and current goals
            for i in range(len(self.user_goals)):
                goal_title = self.user_goals[i]["title"]
                
                if i in self.completed_goals:
                    # Completed goal with checkmark and green styling
                    goal_row = ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
                        ft.Text(
                            f"✓ {goal_title}",
                            size=14,
                            color=ft.Colors.GREEN_700,
                            weight=ft.FontWeight.W_500
                        )
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                elif i == self.current_goal_index:
                    # Current goal with arrow and blue styling
                    goal_row = ft.Row([
                        ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.BLUE, size=20),
                        ft.Text(
                            goal_title,
                            size=14,
                            color=ft.Colors.BLUE_700,
                            weight=ft.FontWeight.BOLD
                        )
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                else:
                    # Pending goal with circle outline and muted styling
                    goal_row = ft.Row([
                        ft.Icon(ft.Icons.RADIO_BUTTON_UNCHECKED, color=ft.Colors.GREY_400, size=20),
                        ft.Text(
                            goal_title,
                            size=14,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                
                progress_container.controls.append(goal_row)
            
            if completed_count >= total_goals and total_goals > 0:
                # Add completion message with celebration styling
                progress_container.controls.append(ft.Divider(height=10))
                progress_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CELEBRATION, color=ft.Colors.AMBER, size=24),
                            ft.Text(
                                config.get_text("all_goals_completed", "¡Felicidades! Has completado todos los objetivos!"),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700
                            )
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                        border_radius=8,
                        padding=10
                    )
                )
                
                # Enable the Finalizar button when all goals are completed
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

        # Show appropriate goal prompt based on current progress
        if self.user_goals and len(self.user_goals) > 0:
            # If we have saved progress, show the current goal prompt
            if self.current_goal_index < len(self.user_goals):
                current_goal = self.user_goals[self.current_goal_index]
                goal_prompt = current_goal.get("prompt", "")
                if goal_prompt:
                    # Apply template substitution if we have extracted info
                    try:
                        formatted_prompt = goal_prompt.format(**self.extracted_info)
                    except KeyError:
                        # If template variables are missing, use original prompt
                        formatted_prompt = goal_prompt
                    
                    scrollable_content.controls.append(ChatMessage(ft.Text(formatted_prompt, selectable=True), is_user=False))
                    self.chat_history.append({"role": "assistant", "content": formatted_prompt})
        
        update_progress_ui()

        async def send_message_click(e):
            user_input = new_message.value
            if not user_input or send_button.disabled:
                return
            
            # 1. Immediately add user message and clear input
            scrollable_content.controls.append(ChatMessage(ft.Text(user_input, selectable=True), is_user=True))
            new_message.value = ""
            send_button.disabled = True
            
            # 2. Add loading indicator and update UI immediately
            loading = LoadingMessage()
            scrollable_content.controls.append(loading)
            self.page.update()

            # 3. Add to chat history
            self.chat_history.append({"role": "user", "content": user_input})

            # 4. Run LLM call in a separate task to avoid blocking
            async def get_llm_response():
                current_goal = self.user_goals[self.current_goal_index]["title"] if self.current_goal_index < len(self.user_goals) else ""
                goal_prompt = self.user_goals[self.current_goal_index].get("prompt", "") if self.current_goal_index < len(self.user_goals) else ""
                
                # Check if current goal has extract_info field
                current_goal_data = self.user_goals[self.current_goal_index] if self.current_goal_index < len(self.user_goals) else {}
                extract_info = current_goal_data.get("extract_info", {})
                
                # Extract information if needed
                if extract_info:
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        loop = asyncio.get_event_loop()
                        extracted_data = await loop.run_in_executor(
                            executor,
                            self.llm_client.extract_information,
                            user_input,
                            extract_info
                        )
                        # Update extracted_info with new data
                        if extracted_data:
                            self.extracted_info.update(extracted_data)
                
                # Wrap the synchronous LLM call in an executor to make it non-blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    full_response = await loop.run_in_executor(
                        executor, 
                        self.llm_client.evaluate_goal_completion, 
                        self.chat_history, 
                        current_goal,
                        goal_prompt
                    )
                return full_response

            # 5. Get the response asynchronously
            try:
                full_response = await get_llm_response()
                
                chat_response = "Hubo un error al procesar la respuesta."
                goal_achieved = False
                
                try:
                    # LLM now only returns goal evaluation, no conversational response
                    if "GOAL_ACHIEVED: true" in full_response:
                        goal_achieved = True
                        # Mark current goal as completed
                        self.completed_goals.add(self.current_goal_index)
                        self.current_goal_index += 1
                        
                        # Save progress after goal completion
                        scenario_id = slide_data.get("scenario_id", "")
                        lesson_id = self.app_state.current_lesson_id
                        self.app_state.save_interactive_scenario_progress(
                            lesson_id, 
                            scenario_id, 
                            self.completed_goals, 
                            self.current_goal_index, 
                            self.extracted_info
                        )
                        
                        # Update progress UI to show completed task
                        update_progress_ui()
                        
                        # If there are more goals, show only the next goal prompt
                        if self.current_goal_index < len(self.user_goals):
                            next_goal = self.user_goals[self.current_goal_index]
                            next_goal_prompt = next_goal.get("prompt", "")
                            if next_goal_prompt:
                                # Apply template substitution if we have extracted info
                                try:
                                    chat_response = next_goal_prompt.format(**self.extracted_info)
                                except KeyError:
                                    # If template variables are missing, use original prompt
                                    chat_response = next_goal_prompt
                            else:
                                # Use a generic continuation message
                                chat_response = "Goed gedaan! Laten we doorgaan."
                        else:
                            # All goals completed
                            chat_response = "Perfect! Je hebt alle doelen bereikt."
                    else:
                        # Goal not achieved, encourage to try again
                        retry_msg = config.get_text("goal_not_achieved", "No es del todo correcto. ¡Inténtalo de nuevo!")
                        chat_response = retry_msg
                        
                except Exception as err:
                    print(f"Error processing LLM response: {err}")
                    chat_response = "Hubo un error al procesar la respuesta."

                # 6. Remove loading and prepare for typing effect
                scrollable_content.controls.remove(loading)
                assistant_text_control = ft.Text(selectable=True)
                scrollable_content.controls.append(ChatMessage(assistant_text_control, is_user=False))
                self.page.update()

                # 7. Simulate typing the response
                await simulate_typing(assistant_text_control, chat_response, self.page)

                self.chat_history.append({"role": "assistant", "content": chat_response})
                
                # 8. Update progress and re-enable inputs if not all goals completed
                update_progress_ui()
                if len(self.completed_goals) < len(self.user_goals):
                     send_button.disabled = False

                self.page.update()
                
            except Exception as e:
                # Handle any errors
                if loading in scrollable_content.controls:
                    scrollable_content.controls.remove(loading)
                error_text = ft.Text(f"Error: {str(e)}", selectable=True)
                scrollable_content.controls.append(ChatMessage(error_text, is_user=False))
                send_button.disabled = False
                self.page.update()

        send_button.on_click = send_message_click
        new_message.on_submit = send_message_click

        def restart_scenario_click(e):
            """Restart the interactive scenario from the beginning."""
            # Clear progress
            self.current_goal_index = 0
            self.completed_goals = set()
            self.extracted_info = {}
            self.chat_history = []
            
            # Clear saved progress
            scenario_id = slide_data.get("scenario_id", "")
            lesson_id = self.app_state.current_lesson_id
            self.app_state.clear_interactive_scenario_progress(lesson_id, scenario_id)
            
            # Clear chat messages (keep title, setting, and progress container)
            # Find the divider and remove everything after it
            divider_index = -1
            for i, control in enumerate(scrollable_content.controls):
                if isinstance(control, ft.Divider):
                    divider_index = i
                    break
            
            if divider_index >= 0:
                # Keep everything up to and including the divider
                scrollable_content.controls = scrollable_content.controls[:divider_index + 1]
            
            # Clear input field and re-enable send button
            new_message.value = ""
            send_button.disabled = False
            
            # Update progress UI and show initial goal prompt
            update_progress_ui()
            
            # Show the first goal prompt if available
            if self.user_goals and len(self.user_goals) > 0:
                current_goal = self.user_goals[0]
                goal_prompt = current_goal.get("prompt", "")
                if goal_prompt:
                    scrollable_content.controls.append(ChatMessage(ft.Text(goal_prompt, selectable=True), is_user=False))
                    self.chat_history.append({"role": "assistant", "content": goal_prompt})
            
            self.page.update()

        restart_button.on_click = restart_scenario_click

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

    def save_current_scenario_progress(self):
        """Save progress for the current interactive scenario if applicable."""
        if hasattr(self, 'user_goals') and hasattr(self, 'completed_goals') and hasattr(self, 'current_goal_index'):
            current_slide = self.app_state.get_current_slide_data()
            if current_slide and current_slide.get("type") == "interactive_scenario":
                scenario_id = current_slide.get("scenario_id", "")
                lesson_id = self.app_state.current_lesson_id
                if hasattr(self, 'extracted_info'):
                    self.app_state.save_interactive_scenario_progress(
                        lesson_id, 
                        scenario_id, 
                        self.completed_goals, 
                        self.current_goal_index, 
                        self.extracted_info
                    )

    def save_current_slide_position(self):
        """Save the current slide position for the lesson."""
        if self.app_state.current_lesson_id:
            self.app_state.lesson_slide_positions[self.app_state.current_lesson_id] = self.app_state.current_slide_index
            self.app_state.save_progress()

    def go_back_to_home(self, e):
        """Go back to home view, saving current progress."""
        # Save current scenario progress
        self.save_current_scenario_progress()
        # Save current slide position
        self.save_current_slide_position()
        # Navigate to home
        self.page.go('/')

    def go_previous(self, e):
        # Save current scenario progress before navigating
        self.save_current_scenario_progress()
        if self.app_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        # Don't proceed if button is disabled
        if self.next_button.disabled:
            return
        
        # Save current scenario progress before navigating
        self.save_current_scenario_progress()
        if self.app_state.next_slide():
            self.update_slide_content()
        else:
            # Mark lesson as completed when finishing
            self.app_state.mark_lesson_completed(self.app_state.current_lesson_id)
            self.page.go('/')