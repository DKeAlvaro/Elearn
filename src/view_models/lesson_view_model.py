# view_models/lesson_view_model.py
import flet as ft
import src.config as config
from src.app_state import AppState
from src.llm_client import LLMClient
import asyncio
from src.ui_components import create_slide_content, ChatMessage, LoadingMessage, InteractiveScenarioSlide, LLMCheckSlide
from src.utils.typing_simulator import simulate_typing

class LessonViewModel:
    def __init__(self, app_state: AppState, llm_client: LLMClient, page: ft.Page, view: ft.View):
        self.app_state = app_state
        self.llm_client = llm_client
        self.page = page
        self.view = view

    def update_slide_content(self):
        current_slide_data = self.app_state.lesson_state.get_current_slide_data()
        if not current_slide_data:
            return

        lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.lesson_state.current_lesson_id)
        is_last_slide = self.app_state.lesson_state.current_slide_index == len(lesson_content) - 1
        self.view.next_button.text = config.get_text("finish", "Finish") if is_last_slide else config.get_text("next", "Next")
        
        if self.app_state.lesson_state.current_slide_index > 0:
            self.view.previous_button.opacity = 1.0
            self.view.previous_button.disabled = False
        else:
            self.view.previous_button.opacity = 0.0
            self.view.previous_button.disabled = True
        
        slide_type = current_slide_data.get("type")
        if slide_type == "interactive_scenario":
            self.view.next_button.disabled = True
        elif is_last_slide:
            if slide_type == "llm_check":
                self.view.next_button.disabled = True
            else:
                self.view.next_button.disabled = False
        else:
            self.view.next_button.disabled = False

        slide_content = create_slide_content(current_slide_data)
        self.view.slide_content_area.content = slide_content
        
        if isinstance(slide_content, InteractiveScenarioSlide):
            self.handle_interactive_scenario(slide_content, current_slide_data)
        elif isinstance(slide_content, LLMCheckSlide):
            self.handle_llm_check(slide_content, current_slide_data)
        
        self.page.update()

    def handle_interactive_scenario(self, slide: InteractiveScenarioSlide, slide_data: dict):
        scenario_state = self.app_state.scenario_state
        scenario_state.scenario_user_goals = slide_data.get("conversation_flow", [])
        
        scenario_id = slide_data.get("scenario_id", "")
        lesson_id = self.app_state.lesson_state.current_lesson_id
        
        saved_progress = self.app_state.progress_manager.get_interactive_scenario_progress(lesson_id, scenario_id)
        if saved_progress:
            scenario_state.scenario_completed_goals = saved_progress['completed_goals']
            scenario_state.scenario_current_goal_index = saved_progress['current_goal_index']
            scenario_state.scenario_extracted_info = saved_progress['extracted_info']
        else:
            scenario_state.reset(self.app_state.progress_manager.save_user_data)

        def update_progress_ui():
            total_goals = len(scenario_state.scenario_user_goals)
            completed_count = len(scenario_state.scenario_completed_goals)
            current_goal_index = scenario_state.scenario_current_goal_index
            
            slide.progress_container.controls.clear()
            
            progress_text = f"Objective {current_goal_index + 1} of {total_goals}"
            slide.progress_container.controls.append(
                ft.Text(progress_text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_600)
            )
            
            if current_goal_index < len(scenario_state.scenario_user_goals):
                current_goal = scenario_state.scenario_user_goals[current_goal_index]
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
            
            self.view.next_button.disabled = True
            
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
                
                self.view.next_button.disabled = False
                lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.lesson_state.current_lesson_id)
                is_last_slide = self.app_state.lesson_state.current_slide_index == len(lesson_content) - 1
                if is_last_slide:
                    self.view.next_button.text = "Finalizar"
                else:
                    self.view.next_button.text = config.get_text("next")
                
                slide.send_button.disabled = True
                slide.new_message.disabled = True
            
            self.page.update()

        if scenario_state.scenario_user_goals:
            if scenario_state.scenario_current_goal_index < len(scenario_state.scenario_user_goals):
                current_goal = scenario_state.scenario_user_goals[scenario_state.scenario_current_goal_index]
                goal_prompt = current_goal.get("chatbot_message", "")
                if goal_prompt:
                    try:
                        all_variables = scenario_state.get_all_available_variables(self.app_state.progress_manager.user_data)
                        formatted_prompt = goal_prompt.format(**all_variables)
                    except KeyError:
                        formatted_prompt = goal_prompt
                    
                    slide.scrollable_content.controls.append(ChatMessage(ft.Text(formatted_prompt, selectable=True), is_user=False))
                    scenario_state.scenario_chat_history.append({"role": "assistant", "content": formatted_prompt})
        
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

            scenario_state.scenario_chat_history.append({"role": "user", "content": user_input})

            async def get_llm_response():
                current_goal_index = scenario_state.scenario_current_goal_index
                current_goal = scenario_state.scenario_user_goals[current_goal_index]["title"] if current_goal_index < len(scenario_state.scenario_user_goals) else ""
                goal_prompt = scenario_state.scenario_user_goals[current_goal_index].get("chatbot_message", "") if current_goal_index < len(scenario_state.scenario_user_goals) else ""
                
                current_goal_data = scenario_state.scenario_user_goals[current_goal_index] if current_goal_index < len(scenario_state.scenario_user_goals) else {}
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
                            scenario_state.scenario_extracted_info.update(extracted_data)
                            self.app_state.progress_manager.save_user_data(extracted_data)
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    full_response = await loop.run_in_executor(
                        executor, 
                        self.llm_client.evaluate_goal_completion, 
                        scenario_state.scenario_chat_history, 
                        current_goal,
                        goal_prompt
                    )
                return full_response

            try:
                full_response = await get_llm_response()
                
                chat_response = "Hubo un error al procesar la respuesta."
                
                try:
                    if "GOAL_ACHIEVED: true" in full_response:
                        scenario_state.scenario_completed_goals.add(scenario_state.scenario_current_goal_index)
                        scenario_state.scenario_current_goal_index += 1
                        
                        self.app_state.progress_manager.save_interactive_scenario_progress(
                            lesson_id, 
                            scenario_id, 
                            scenario_state.scenario_completed_goals, 
                            scenario_state.scenario_current_goal_index, 
                            scenario_state.scenario_extracted_info
                        )
                        
                        update_progress_ui()
                        
                        if scenario_state.scenario_current_goal_index < len(scenario_state.scenario_user_goals):
                            next_goal = scenario_state.scenario_user_goals[scenario_state.scenario_current_goal_index]
                            next_goal_prompt = next_goal.get("chatbot_message", "")
                            if next_goal_prompt:
                                try:
                                    all_variables = scenario_state.get_all_available_variables(self.app_state.progress_manager.user_data)
                                    chat_response = next_goal_prompt.format(**all_variables)
                                except KeyError:
                                    chat_response = next_goal_prompt
                            else:
                                chat_response = "Goed gedaan! Laten we doorgaan."
                        else:
                            chat_response = "Perfect! Je hebt alle doelen bereikt."
                    elif "GOAL_ACHIEVED: false" in full_response:
                        # Check if this is an API error (contains error message after GOAL_ACHIEVED: false)
                        lines = full_response.split('\n')
                        if len(lines) > 1 and lines[1].strip():
                            # There's an error message after GOAL_ACHIEVED: false, display it
                            error_message = '\n'.join(lines[1:]).strip()
                            chat_response = f"Error: {error_message}"
                        else:
                            # Regular goal not achieved, show retry message
                            retry_msg = config.get_text("goal_not_achieved", "Not quite right. Try again!")
                            chat_response = retry_msg
                    else:
                        # Unexpected response format, display it as an error
                        chat_response = f"Error: {full_response}"
                        
                except Exception as err:
                    print(f"Error processing LLM response: {err}")
                    chat_response = "Hubo un error al procesar la respuesta."

                slide.scrollable_content.controls.remove(loading)
                assistant_text_control = ft.Text(selectable=True)
                slide.scrollable_content.controls.append(ChatMessage(assistant_text_control, is_user=False))
                self.page.update()

                await simulate_typing(assistant_text_control, chat_response, self.page)

                scenario_state.scenario_chat_history.append({"role": "assistant", "content": chat_response})
                
                update_progress_ui()
                if len(scenario_state.scenario_completed_goals) < len(scenario_state.scenario_user_goals):
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
            scenario_state.reset(self.app_state.progress_manager.save_user_data)
            self.app_state.progress_manager.clear_interactive_scenario_progress(lesson_id, scenario_id)
            
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
            
            if scenario_state.scenario_user_goals:
                current_goal = scenario_state.scenario_user_goals[0]
                goal_prompt = current_goal.get("chatbot_message", "")
                if goal_prompt:
                    try:
                        all_variables = scenario_state.get_all_available_variables(self.app_state.progress_manager.user_data)
                        formatted_prompt = goal_prompt.format(**all_variables)
                    except KeyError:
                        formatted_prompt = goal_prompt
                    
                    slide.scrollable_content.controls.append(ChatMessage(ft.Text(formatted_prompt, selectable=True), is_user=False))
                    scenario_state.scenario_chat_history.append({"role": "assistant", "content": formatted_prompt})
            
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
            
            lesson_content = self.app_state.data_manager.get_lesson_content(self.app_state.lesson_state.current_lesson_id)
            is_last_slide = self.app_state.lesson_state.current_slide_index == len(lesson_content) - 1
            if is_last_slide:
                self.view.next_button.disabled = False
            
            self.page.update()

        slide.check_button.on_click = check_answer_click

    def go_back_to_home(self, e):
        self.app_state.lesson_state.save_current_slide_position()
        self.page.go('/')

    def go_previous(self, e):
        if self.app_state.lesson_state.previous_slide():
            self.update_slide_content()

    def go_next(self, e):
        if self.view.next_button.disabled:
            return
        
        if self.app_state.lesson_state.next_slide():
            self.update_slide_content()
        else:
            self.app_state.progress_manager.mark_lesson_completed(self.app_state.lesson_state.current_lesson_id)
            self.page.go('/')