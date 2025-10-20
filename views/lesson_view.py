# views/lesson_view.py
import flet as ft
from app_state import AppState
from ui_components import create_slide_content, ChatMessage, LoadingMessage, InteractiveScenarioSlide, LLMCheckSlide, CustomAppBar
from utils.typing_simulator import simulate_typing
from llm_client import LLMClient
import config
import asyncio


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
            config.get_text("previous"), 
            on_click=self.go_previous, 
            visible=True,
            disabled=True,
            opacity=0.0
        )
        self.next_button = ft.ElevatedButton(text=config.get_text("next", "Siguiente"), on_click=self.go_next)

        self.controls = [
            CustomAppBar(
                title=self.app_state.get_current_lesson_title(),
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
        
        self.update_slide_content()

    def update_slide_content(self):
        current_slide_data = self.app_state.get_current_slide_data()
        if not current_slide_data:
            return

        lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
        is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
        self.next_button.text = config.get_text("finish", "Finalizar") if is_last_slide else config.get_text("next", "Siguiente")
        
        if self.app_state.current_slide_index > 0:
            self.previous_button.opacity = 1.0
            self.previous_button.disabled = False
        else:
            self.previous_button.opacity = 0.0
            self.previous_button.disabled = True
        
        slide_type = current_slide_data.get("type")
        if slide_type == "interactive_scenario":
            # Interactive scenarios start with next button disabled
            self.next_button.disabled = True
        elif is_last_slide:
            if slide_type == "llm_check":
                self.next_button.disabled = True
            else:
                self.next_button.disabled = False
        else:
            self.next_button.disabled = False

        slide_content = create_slide_content(current_slide_data)
        self.slide_content_area.content = slide_content
        
        if isinstance(slide_content, InteractiveScenarioSlide):
            self.handle_interactive_scenario(slide_content, current_slide_data)
        elif isinstance(slide_content, LLMCheckSlide):
            self.handle_llm_check(slide_content, current_slide_data)
        
        self.page.update()

    def handle_interactive_scenario(self, slide: InteractiveScenarioSlide, slide_data: dict):
        self.app_state.scenario_user_goals = slide_data.get("conversation_flow", [])
        
        scenario_id = slide_data.get("scenario_id", "")
        lesson_id = self.app_state.current_lesson_id
        
        saved_progress = self.app_state.get_interactive_scenario_progress(lesson_id, scenario_id)
        if saved_progress:
            self.app_state.scenario_completed_goals = saved_progress['completed_goals']
            self.app_state.scenario_current_goal_index = saved_progress['current_goal_index']
            self.app_state.scenario_extracted_info = saved_progress['extracted_info']
        else:
            self.app_state.reset_scenario_state()

        def update_progress_ui():
            total_goals = len(self.app_state.scenario_user_goals)
            completed_count = len(self.app_state.scenario_completed_goals)
            current_goal_index = self.app_state.scenario_current_goal_index
            
            slide.progress_container.controls.clear()
            
            # Show progress indicator
            progress_text = f"Objective {current_goal_index + 1} of {total_goals}"
            slide.progress_container.controls.append(
                ft.Text(progress_text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_600)
            )
            
            # Show only the current objective
            if current_goal_index < len(self.app_state.scenario_user_goals):
                current_goal = self.app_state.scenario_user_goals[current_goal_index]
                goal_title = current_goal["title"]
                
                goal_row = ft.Row([
                    ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.BLUE, size=20),
                    ft.Text(
                        goal_title, 
                        size=16, 
                        color=ft.Colors.BLUE_700, 
                        weight=ft.FontWeight.BOLD,
                        expand=True,
                        text_align=ft.TextAlign.LEFT
                    )
                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START)
                
                slide.progress_container.controls.append(goal_row)
            
            # Always disable next button initially for interactive scenarios
            self.next_button.disabled = True
            
            if completed_count >= total_goals and total_goals > 0:
                slide.progress_container.controls.append(ft.Divider(height=10))
                slide.progress_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CELEBRATION, color=ft.Colors.AMBER, size=24),
                            ft.Text(
                                config.get_text("all_goals_completed"), 
                                size=16, 
                                weight=ft.FontWeight.BOLD, 
                                color=ft.Colors.GREEN_700,
                                expand=True,
                                text_align=ft.TextAlign.LEFT
                            )
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                        border_radius=8,
                        padding=10
                    )
                )
                
                # Only enable next button when all goals are completed
                self.next_button.disabled = False
                lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
                is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
                if is_last_slide:
                    self.next_button.text = "Finalizar"
                else:
                    self.next_button.text = config.get_text("next")
                
                slide.send_button.disabled = True
                slide.new_message.disabled = True
            
            self.page.update()

        if self.app_state.scenario_user_goals:
            if self.app_state.scenario_current_goal_index < len(self.app_state.scenario_user_goals):
                current_goal = self.app_state.scenario_user_goals[self.app_state.scenario_current_goal_index]
                goal_prompt = current_goal.get("chatbot_message", "")
                if goal_prompt:
                    try:
                        # Use all available variables (global + scenario)
                        all_variables = self.app_state.get_all_available_variables()
                        formatted_prompt = goal_prompt.format(**all_variables)
                    except KeyError:
                        formatted_prompt = goal_prompt
                    
                    slide.scrollable_content.controls.append(ChatMessage(ft.Text(formatted_prompt, selectable=True), is_user=False))
                    self.app_state.scenario_chat_history.append({"role": "assistant", "content": formatted_prompt})
        
        update_progress_ui()

        async def send_message_click(e):
            user_input = slide.new_message.value
            if not user_input or slide.send_button.disabled:
                return
            
            slide.scrollable_content.controls.append(ChatMessage(ft.Text(user_input, selectable=True), is_user=True))
            slide.new_message.value = ""
            slide.send_button.disabled = True
            
            loading = LoadingMessage()
            slide.scrollable_content.controls.append(loading)
            self.page.update()

            self.app_state.scenario_chat_history.append({"role": "user", "content": user_input})

            async def get_llm_response():
                current_goal_index = self.app_state.scenario_current_goal_index
                current_goal = self.app_state.scenario_user_goals[current_goal_index]["title"] if current_goal_index < len(self.app_state.scenario_user_goals) else ""
                goal_prompt = self.app_state.scenario_user_goals[current_goal_index].get("chatbot_message", "") if current_goal_index < len(self.app_state.scenario_user_goals) else ""
                
                current_goal_data = self.app_state.scenario_user_goals[current_goal_index] if current_goal_index < len(self.app_state.scenario_user_goals) else {}
                extract_info = current_goal_data.get("extract_info", {})
                
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
                        if extracted_data:
                            self.app_state.scenario_extracted_info.update(extracted_data)
                            # Save extracted data to global user data storage
                            self.app_state.save_user_data(extracted_data)
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    full_response = await loop.run_in_executor(
                        executor, 
                        self.llm_client.evaluate_goal_completion, 
                        self.app_state.scenario_chat_history, 
                        current_goal,
                        goal_prompt
                    )
                return full_response

            try:
                full_response = await get_llm_response()
                
                chat_response = "Hubo un error al procesar la respuesta."
                
                try:
                    if "GOAL_ACHIEVED: true" in full_response:
                        self.app_state.scenario_completed_goals.add(self.app_state.scenario_current_goal_index)
                        self.app_state.scenario_current_goal_index += 1
                        
                        self.app_state.save_interactive_scenario_progress(
                            lesson_id, 
                            scenario_id, 
                            self.app_state.scenario_completed_goals, 
                            self.app_state.scenario_current_goal_index, 
                            self.app_state.scenario_extracted_info
                        )
                        
                        update_progress_ui()
                        
                        if self.app_state.scenario_current_goal_index < len(self.app_state.scenario_user_goals):
                            next_goal = self.app_state.scenario_user_goals[self.app_state.scenario_current_goal_index]
                            next_goal_prompt = next_goal.get("chatbot_message", "")
                            if next_goal_prompt:
                                try:
                                    # Use all available variables (global + scenario)
                                    all_variables = self.app_state.get_all_available_variables()
                                    chat_response = next_goal_prompt.format(**all_variables)
                                except KeyError:
                                    chat_response = next_goal_prompt
                            else:
                                chat_response = "Goed gedaan! Laten we doorgaan."
                        else:
                            chat_response = "Perfect! Je hebt alle doelen bereikt."
                    else:
                        retry_msg = config.get_text("goal_not_achieved", "No es del todo correcto. ¡Inténtalo de nuevo!")
                        chat_response = retry_msg
                        
                except Exception as err:
                    print(f"Error processing LLM response: {err}")
                    chat_response = "Hubo un error al procesar la respuesta."

                slide.scrollable_content.controls.remove(loading)
                assistant_text_control = ft.Text(selectable=True)
                slide.scrollable_content.controls.append(ChatMessage(assistant_text_control, is_user=False))
                self.page.update()

                await simulate_typing(assistant_text_control, chat_response, self.page)

                self.app_state.scenario_chat_history.append({"role": "assistant", "content": chat_response})
                
                update_progress_ui()
                if len(self.app_state.scenario_completed_goals) < len(self.app_state.scenario_user_goals):
                     slide.send_button.disabled = False

                self.page.update()
                
            except Exception as e:
                if loading in slide.scrollable_content.controls:
                    slide.scrollable_content.controls.remove(loading)
                error_text = ft.Text(f"Error: {str(e)}", selectable=True)
                slide.scrollable_content.controls.append(ChatMessage(error_text, is_user=False))
                slide.send_button.disabled = False
                self.page.update()

        slide.send_button.on_click = send_message_click
        slide.new_message.on_submit = send_message_click

        def restart_scenario_click(e):
            self.app_state.reset_scenario_state()
            self.app_state.clear_interactive_scenario_progress(lesson_id, scenario_id)
            
            divider_index = -1
            for i, control in enumerate(slide.scrollable_content.controls):
                if isinstance(control, ft.Divider):
                    divider_index = i
                    break
            
            if divider_index >= 0:
                slide.scrollable_content.controls = slide.scrollable_content.controls[:divider_index + 1]
            
            slide.new_message.value = ""
            slide.send_button.disabled = False
            slide.new_message.disabled = False
            
            update_progress_ui()
            
            if self.app_state.scenario_user_goals:
                current_goal = self.app_state.scenario_user_goals[0]
                goal_prompt = current_goal.get("chatbot_message", "")
                if goal_prompt:
                    try:
                        # Use all available variables (global + scenario)
                        all_variables = self.app_state.get_all_available_variables()
                        formatted_prompt = goal_prompt.format(**all_variables)
                    except KeyError:
                        formatted_prompt = goal_prompt
                    
                    slide.scrollable_content.controls.append(ChatMessage(ft.Text(formatted_prompt, selectable=True), is_user=False))
                    self.app_state.scenario_chat_history.append({"role": "assistant", "content": formatted_prompt})
            
            self.page.update()

        slide.restart_button.on_click = restart_scenario_click

    def handle_llm_check(self, slide: LLMCheckSlide, slide_data: dict):
        def check_answer_click(e):
            user_input = slide.answer_field.value
            if not user_input:
                return
            
            slide.check_button.disabled = True
            slide.result_text.value = "Pensando..."
            self.page.update()

            correction = self.llm_client.get_correction(user_input, slide_data["chatbot_message"])
            
            slide.result_text.value = correction
            slide.check_button.disabled = False
            
            lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.current_lesson_id)
            is_last_slide = self.app_state.current_slide_index == len(lesson_content) - 1
            if is_last_slide:
                self.next_button.disabled = False
            
            self.page.update()

        slide.check_button.on_click = check_answer_click

    def save_current_scenario_progress(self):
        current_slide = self.app_state.get_current_slide_data()
        if current_slide and current_slide.get("type") == "interactive_scenario":
            scenario_id = current_slide.get("scenario_id", "")
            lesson_id = self.app_state.current_lesson_id
            self.app_state.save_interactive_scenario_progress(
                lesson_id, 
                scenario_id, 
                self.app_state.scenario_completed_goals, 
                self.app_state.scenario_current_goal_index, 
                self.app_state.scenario_extracted_info
            )

    def save_current_slide_position(self):
        if self.app_state.current_lesson_id:
            self.app_state.lesson_slide_positions[self.app_state.current_lesson_id] = self.app_state.current_slide_index
            self.app_state.save_progress()

    def go_back_to_home(self, e):
        self.save_current_scenario_progress()
        self.save_current_slide_position()
        self.page.go('/')

    def go_previous(self, e):
        self.save_current_scenario_progress()
        if self.app_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        if self.next_button.disabled:
            return
        
        self.save_current_scenario_progress()
        if self.app_state.next_slide():
            self.update_slide_content()
        else:
            self.app_state.mark_lesson_completed(self.app_state.current_lesson_id)
            self.page.go('/')