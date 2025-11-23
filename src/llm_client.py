# llm_client.py
import src.config as config
from typing import List, Dict
import json
import openai

# Safely import Gradio client to avoid crashing if the package isn't available
try:
    from gradio_client import Client
    print("Successfully imported gradio_client")
except Exception as e:
    print(f"Failed to import gradio_client: {e}")
    Client = None

class LLMClient:
    def __init__(self):
        self.openai_client = None
        self.gradio_client = None
        self.api_key_valid = False
        self.using_deepseek = False
        self.active = False
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize both OpenAI and Gradio clients"""
        # Initialize Gradio client (always available as fallback)
        try:
            if Client is not None:
                self.gradio_client = Client("huggingface-projects/llama-3.2-3B-Instruct")
        except Exception as e:
            print(f"Warning: Could not initialize Gradio client: {e}")
        
        # Try to initialize OpenAI client if API key is available
        self.update_api_key()
    
    def validate_api_key(self, api_key: str = None) -> bool:
        """Validate if the API key works by making a test request"""
        if not api_key:
            api_key = config.get_effective_api_key()
        
        if not api_key:
            return False
        
        try:
            test_client = openai.OpenAI(
                api_key=api_key,
                base_url=config.BASE_URL
            )
            
            # Make a minimal test request
            response = test_client.chat.completions.create(
                model=config.MODEL,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0.1
            )
            
            return True
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False
    
    def update_api_key(self):
        """Update API key and determine which client to use"""
        api_key = config.get_effective_api_key()
        
        if api_key and self.validate_api_key(api_key):
            try:
                self.openai_client = openai.OpenAI(
                    api_key=api_key,
                    base_url=config.BASE_URL
                )
                self.api_key_valid = True
                self.using_deepseek = True
                self.active = True
                print("Using DeepSeek API")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.api_key_valid = False
                self.using_deepseek = False
                # Fall back to Gradio if available
                if self.gradio_client is not None:
                    self.active = True
                    print("Falling back to Gradio client")
                else:
                    self.active = False
        else:
            self.api_key_valid = False
            self.using_deepseek = False
            # Use Gradio as fallback
            if self.gradio_client is not None:
                self.active = True
                print("Using Gradio client (fallback)")
            else:
                self.active = False
                print("No LLM client available")
    
    def get_api_status(self) -> dict:
        """Get current API status for UI display"""
        return {
            "has_api_key": config.get_effective_api_key() is not None,
            "api_key_valid": self.api_key_valid,
            "using_deepseek": self.using_deepseek,
            "using_gradio": not self.using_deepseek and self.active
        }
    
    def is_deepseek_active(self) -> bool:
        """Check if DeepSeek API is currently active"""
        return self.using_deepseek and self.api_key_valid
    
    def _format_messages_for_gradio(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt string for Gradio"""
        formatted_prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted_prompt += f"System: {content}\n\n"
            elif role == "user":
                formatted_prompt += f"User: {content}\n\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n\n"
        
        # Add final prompt for assistant response
        formatted_prompt += "Assistant:"
        return formatted_prompt
    
    def _call_gradio_client(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> str:
        """Make a call to the Gradio client with the given prompt"""
        try:
            result = self.gradio_client.predict(
                message=prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                api_name="/chat"
            )
            return result
        except Exception as e:
            # Let the calling method handle error logging to avoid duplicates
            raise e

    def get_scenario_response(self, history: List[Dict[str, str]], concepts_to_check: Dict[str, str]):
        """
        Gets a response from the LLM for a scenario, asking it to evaluate concepts.
        """
        if not self.active:
            return f"CONCEPTS_COVERED: []\n{config.get_text('llm_not_configured_scenario', 'LLM client not configured.')}"

        # Get the target language from configuration
        language_info = config.get_language_info()
        target_language = language_info["target_language_folder"].title()

        # Convert the concepts dict to a string for the chatbot_message
        concepts_json_str = json.dumps(concepts_to_check, ensure_ascii=False)

        system_prompt = config.get_text(
            "scenario_system_prompt",
            "You are a language assistant. Your main goal is to have a natural conversation in {target_language} with the user to help them practice.\n\nCRITICAL CONSTRAINT: In your conversational responses, you can ONLY use words and phrases from the following lesson concepts: {concepts}. Do not use any {target_language} words that are not on this list. If you need to communicate something that is not in the concepts, use Spanish or English.\n\nYou have a VERY IMPORTANT AND HIDDEN SECONDARY TASK.\nBefore writing your conversational response, you MUST analyze the user's last message to see if they have used any of the following concepts: {concepts}.\nDon't be too strict; if the user uses a close form or a key part of the phrase, count it as valid.\n\nYour response MUST follow this EXACT format:\n1. A line starting with `CONCEPTS_COVERED: ` followed by a JSON list of the `item_id`s of the concepts the user JUST used. If they used none, the list should be empty `[]`.\n2. A newline character `\n`.\n3. Your normal conversational response in {target_language} (ONLY using concepts from the list).\n\nExample 1 (user uses concepts):\nCONCEPTS_COVERED: [\"L01_V01\", \"L01_G01\"]\nJa, natuurlijk. Een momentje.\n\nExample 2 (user does not use concepts):\nCONCEPTS_COVERED: []\nHallo! Wat kan ik voor je doen?\n\nNEVER mention the concepts or this secondary task to the user. Just act your role and provide the control line at the beginning."
        ).format(target_language=target_language, concepts=concepts_json_str)
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        # Print the LLM input to console for debugging
        print("\n" + "="*50)
        print("LLM INPUT:")
        print("="*50)
        print("SYSTEM PROMPT:")
        print(system_prompt)
        print("\nCONVERSATION HISTORY:")
        for i, msg in enumerate(history):
            print(f"{i+1}. {msg['role'].upper()}: {msg['content']}")
        print("="*50 + "\n")

        try:
            if self.using_deepseek and self.openai_client:
                # Use DeepSeek API
                response = self.openai_client.chat.completions.create(
                    model=config.MODEL,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
            else:
                # Use Gradio fallback
                prompt = self._format_messages_for_gradio(messages)
                response_text = self._call_gradio_client(prompt, max_tokens=150, temperature=0.7)
            
            # Print the LLM response to console for debugging
            print("LLM RESPONSE:")
            print("-" * 30)
            print(response_text)
            print("-" * 30 + "\n")
            
            return response_text
        except Exception as e:
            error_type = "deepseek_api_error" if self.using_deepseek else "gradio_api_error"
            print(config.get_text(error_type, "Error in API call: {error}").format(error=str(e)))
            return f"CONCEPTS_COVERED: []\n{config.get_text('api_error_scenario', 'There was an error contacting the AI service.')}"

    def extract_information(self, user_message: str, extract_info: Dict[str, str]):
        """
        Extract specific information from user message based on extract_info specifications.
        Returns a dictionary with extracted values.
        """
        if not self.active:
            return {}

        if not extract_info:
            return {}

        # Get the target language from configuration
        language_info = config.get_language_info()
        target_language = language_info["target_language_code"].title()

        # Build extraction instructions
        extraction_instructions = []
        for key, description in extract_info.items():
            extraction_instructions.append(f"- {key}: {description}")
        
        instructions_text = "\n".join(extraction_instructions)

        system_prompt = config.get_text(
            "info_extraction_system_prompt",
            "You are an information extraction assistant. The user is learning {target_language}. Extract the following information from the user's message:\n\n{instructions}\n\nRespond with ONLY a JSON object containing the extracted values. If you cannot extract a value, use null. Example: {{\"user_name\": \"John\", \"age\": null}}"
        ).format(target_language=target_language, instructions=instructions_text)

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if self.using_deepseek and self.openai_client:
                # Use DeepSeek API
                response = self.openai_client.chat.completions.create(
                    model=config.MODEL,
                    messages=messages,
                    max_tokens=100,
                    temperature=0.1
                )
                response_text = response.choices[0].message.content.strip()
            else:
                # Use Gradio fallback
                prompt = self._format_messages_for_gradio(messages)
                response_text = self._call_gradio_client(prompt, max_tokens=100, temperature=0.1).strip()
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response_text)
                return extracted_data
            except json.JSONDecodeError:
                print(f"Failed to parse extraction response as JSON: {response_text}")
                return {}
                
        except Exception as e:
            error_type = "deepseek_api_error" if self.using_deepseek else "gradio_api_error"
            print(config.get_text(error_type, "Error in API call: {error}").format(error=str(e)))
            return {}

    def evaluate_goal_completion(self, history: List[Dict[str, str]], current_goal: str, goal_prompt: str = ""):
        """
        Evaluates if the user has completed the current goal based on their last message.
        Returns a response with GOAL_ACHIEVED: true/false and a conversational response.
        """
        if not self.active:
            return f"GOAL_ACHIEVED: false\n{config.get_text('llm_not_configured_scenario', 'LLM client not configured.')}"

        # Get the target language from configuration
        language_info = config.get_language_info()
        target_language = language_info["target_language_folder"].title()
        
        system_prompt = config.get_text(
            "goal_evaluation_system_prompt",
            "You are a language learning goal evaluator. Your ONLY task is to evaluate if the user has completed the following goal: '{goal}'. Respond with EXACTLY one line: GOAL_ACHIEVED: true (if completed) or GOAL_ACHIEVED: false (if not completed)."
        ).format(goal=current_goal, target_language=target_language)
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        # Print the LLM input to console for debugging
        print("\n" + "="*50)
        print("GOAL EVALUATION INPUT:")
        print("="*50)
        print("SYSTEM PROMPT:")
        print(system_prompt)
        print("\nCONVERSATION HISTORY:")
        for i, msg in enumerate(history):
            print(f"{i+1}. {msg['role'].upper()}: {msg['content']}")
        print("="*50 + "\n")

        try:
            if self.using_deepseek and self.openai_client:
                # Use DeepSeek API
                response = self.openai_client.chat.completions.create(
                    model=config.MODEL,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
            else:
                # Use Gradio fallback
                prompt = self._format_messages_for_gradio(messages)
                response_text = self._call_gradio_client(prompt, max_tokens=150, temperature=0.7)
            
            # Print the LLM response to console for debugging
            print("GOAL EVALUATION RESPONSE:")
            print("-" * 30)
            print(response_text)
            print("-" * 30 + "\n")
            
            return response_text
        except Exception as e:
            error_type = "deepseek_api_error" if self.using_deepseek else "gradio_api_error"
            print(config.get_text(error_type, "Error in API call: {error}").format(error=str(e)))
            original_error = str(e)
            return f"GOAL_ACHIEVED: false\n{original_error}\n\nUse your own API key to avoid connection issues!"

    def get_correction(self, user_answer: str, prompt_question: str):
        if not self.active:
            return config.get_text("llm_not_configured", "LLM client not configured. Please check your connection.")

        system_prompt = config.get_text(
            "correction_system_prompt",
            "You are a friendly and concise language teacher. The user is learning and will give you an answer to a question. Your task is to: \n1. Evaluate if the user\'s answer is correct for the given question.\n2. If it is correct, praise them briefly (e.g., 'Perfect!', 'Very good!').\n3. If it is incorrect, correct them simply and directly, explaining the reason for the error in a single sentence.\nAlways respond in the UI language."
        )

        user_message = config.get_text(
            "correction_question_template",
            "The question was: '{question}'. My answer was: '{answer}'."
        ).format(question=prompt_question, answer=user_answer)

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if self.using_deepseek and self.openai_client:
                # Use DeepSeek API
                response = self.openai_client.chat.completions.create(
                    model=config.MODEL,
                    messages=messages,
                    max_tokens=100,
                    temperature=0.7
                )
                response_text = response.choices[0].message.content
            else:
                # Use Gradio fallback
                prompt = self._format_messages_for_gradio(messages)
                response_text = self._call_gradio_client(prompt, max_tokens=100, temperature=0.7)
            
            return response_text
        except Exception as e:
            error_type = "deepseek_api_error" if self.using_deepseek else "gradio_api_error"
            print(config.get_text(error_type, "Error in API call: {error}").format(error=str(e)))
            return config.get_text("api_error", "There was an error contacting the AI service.")