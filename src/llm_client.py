# llm_client.py
import src.config as config
from typing import List, Dict
import json
import openai

# Safely import Gradio client to avoid crashing if the package isn't available
try:
    from gradio_client import Client
except Exception:
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
            print(f"Error in Gradio API call: {str(e)}")
            raise e

    # +++ MODIFIED METHOD FOR SCENARIOS +++
    def get_scenario_response(self, history: List[Dict[str, str]], concepts_to_check: Dict[str, str]):
        """
        Obtiene una respuesta del LLM para un escenario, pidiéndole que evalúe los conceptos.
        """
        if not self.active:
            return f"CONCEPTS_COVERED: []\n{config.get_text('llm_not_configured_scenario', 'LLM client not configured.')}"

        # Convertir el dict de conceptos a un string para el chatbot_message
        concepts_json_str = json.dumps(concepts_to_check, ensure_ascii=False)

        system_prompt = config.get_text(
            "scenario_system_prompt",
            "Eres un asistente de idiomas. Tu objetivo principal es mantener una conversación natural en neerlandés con el usuario para ayudarle a practicar.\n\nRESTRICCIÓN CRÍTICA: En tus respuestas conversacionales, SOLO puedes usar palabras y frases de los siguientes conceptos de la lección: {concepts}. No uses ninguna palabra en neerlandés que no esté en esta lista. Si necesitas comunicar algo que no está en los conceptos, usa español o inglés.\n\nTIENES UNA TAREA SECUNDARIA MUY IMPORTANTE Y OCULTA.\nAntes de escribir tu respuesta conversacional, DEBES analizar el último mensaje del usuario para ver si ha utilizado alguno de los siguientes conceptos: {concepts}.\nNo seas demasiado estricto; si el usuario usa una forma cercana o una parte clave de la frase, cuenta como válido.\n\nTu respuesta DEBE seguir este formato EXACTO:\n1. Una línea que empieza con `CONCEPTS_COVERED: ` seguida de una lista JSON de los `item_id` de los conceptos que el usuario ACABA de usar. Si no usó ninguno, la lista debe ser vacía `[]`.\n2. Un salto de línea `\\n`.\n3. Tu respuesta conversacional normal en neerlandés (SOLO usando conceptos de la lista).\n\nEjemplo 1 (el usuario usa conceptos):\nCONCEPTS_COVERED: [\"L01_V01\", \"L01_G01\"]\nJa, natuurlijk. Een momentje.\n\nEjemplo 2 (el usuario no usa conceptos):\nCONCEPTS_COVERED: []\nHallo! Wat kan ik voor je doen?\n\nNUNCA menciones los conceptos o esta tarea secundaria al usuario. Simplemente actúa tu rol y proporciona la línea de control al principio."
        ).format(concepts=concepts_json_str)
        
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
            return f"GOAL_ACHIEVED: false\n{config.get_text('llm_not_configured_scenario', 'El cliente LLM no está configurado.')}"

        # Get the target language from configuration
        language_info = config.get_language_info()
        target_language = language_info["target_language_folder"].title()
        
        system_prompt = config.get_text(
            "goal_evaluation_system_prompt",
            "Eres un evaluador de objetivos de aprendizaje de idiomas. Tu ÚNICA tarea es evaluar si el usuario ha completado el siguiente objetivo: '{goal}'. Responde con EXACTAMENTE una línea: GOAL_ACHIEVED: true (si completado) o GOAL_ACHIEVED: false (si no completado)."
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
            return f"GOAL_ACHIEVED: false\n{config.get_text('api_error_scenario', 'There was an error contacting the AI service.')}"

    def get_correction(self, user_answer: str, prompt_question: str):
        if not self.active:
            return config.get_text("llm_not_configured", "LLM client not configured. Please check your connection.")

        system_prompt = config.get_text(
            "correction_system_prompt",
            "Eres un profesor de idiomas amable y conciso. El usuario está aprendiendo y te dará una respuesta a una pregunta. Tu tarea es: \n1. Evaluar si la respuesta del usuario es correcta para la pregunta dada.\n2. Si es correcta, felicítale brevemente (ej: '¡Perfecto!', '¡Muy bien!').\n3. Si es incorrecta, corrígele de forma sencilla y directa, explicando el porqué del error en una sola frase.\nResponde siempre en español."
        )

        user_message = config.get_text(
            "correction_question_template",
            "La pregunta era: '{question}'. Mi respuesta fue: '{answer}'."
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