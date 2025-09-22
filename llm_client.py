# llm_client.py
import config
from openai import OpenAI
from typing import List, Dict
import json

class LLMClient:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=config.get_effective_api_key(),
                base_url=config.DEEPSEEK_BASE_URL
            )
            self.active = True
        except Exception as e:
            print(config.get_text("llm_init_error", "Error al inicializar el cliente de OpenAI: {error}").format(error=str(e)))
            self.active = False
    
    def update_api_key(self):
        """Update the API key for the client"""
        try:
            self.client = OpenAI(
                api_key=config.get_effective_api_key(),
                base_url=config.DEEPSEEK_BASE_URL
            )
            self.active = True
        except Exception as e:
            print(config.get_text("llm_init_error", "Error al inicializar el cliente de OpenAI: {error}").format(error=str(e)))
            self.active = False
    
    # +++ MODIFIED METHOD FOR SCENARIOS +++
    def get_scenario_response(self, history: List[Dict[str, str]], concepts_to_check: Dict[str, str]):
        """
        Obtiene una respuesta del LLM para un escenario, pidiéndole que evalúe los conceptos.
        """
        if not self.active or not config.get_effective_api_key():
            return f"CONCEPTS_COVERED: []\n{config.get_text('llm_not_configured_scenario', 'El cliente LLM no está configurado.')}"

        # Convertir el dict de conceptos a un string para el prompt
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
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            response = chat_completion.choices[0].message.content
            
            # Print the LLM response to console for debugging
            print("LLM RESPONSE:")
            print("-" * 30)
            print(response)
            print("-" * 30 + "\n")
            
            return response
        except Exception as e:
            print(config.get_text("deepseek_api_error", "Error en la llamada a la API de DeepSeek: {error}").format(error=str(e)))
            return f"CONCEPTS_COVERED: []\n{config.get_text('api_error_scenario', 'Hubo un error al contactar con el servicio de IA.')}"

    def extract_information(self, user_message: str, extract_info: Dict[str, str]):
        """
        Extract specific information from user message based on extract_info specifications.
        Returns a dictionary with extracted values.
        """
        if not self.active or not config.get_effective_api_key():
            return {}

        if not extract_info:
            return {}

        # Get the target language from configuration
        language_config = config.get_current_config()
        target_language = language_config["target_language"]

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
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=100,
                temperature=0.1
            )
            response = chat_completion.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response)
                return extracted_data
            except json.JSONDecodeError:
                print(f"Failed to parse extraction response as JSON: {response}")
                return {}
                
        except Exception as e:
            print(config.get_text("deepseek_api_error", "Error en la llamada a la API de DeepSeek: {error}").format(error=str(e)))
            return {}

    def evaluate_goal_completion(self, history: List[Dict[str, str]], current_goal: str, goal_prompt: str = ""):
        """
        Evaluates if the user has completed the current goal based on their last message.
        Returns a response with GOAL_ACHIEVED: true/false and a conversational response.
        """
        if not self.active or not config.get_effective_api_key():
            return f"GOAL_ACHIEVED: false\n{config.get_text('llm_not_configured_scenario', 'El cliente LLM no está configurado.')}"

        # Get the target language from configuration
        language_config = config.get_current_config()
        target_language = language_config["target_language"]
        
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
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            response = chat_completion.choices[0].message.content
            
            # Print the LLM response to console for debugging
            print("GOAL EVALUATION RESPONSE:")
            print("-" * 30)
            print(response)
            print("-" * 30 + "\n")
            
            return response
        except Exception as e:
            print(config.get_text("deepseek_api_error", "Error en la llamada a la API de DeepSeek: {error}").format(error=str(e)))
            return f"GOAL_ACHIEVED: false\n{config.get_text('api_error_scenario', 'Hubo un error al contactar con el servicio de IA.')}"

    def get_correction(self, user_answer: str, prompt_question: str):
        if not self.active or not config.get_effective_api_key():
            return config.get_text("llm_not_configured", "El cliente LLM no está configurado. Por favor, añade tu API key en config.py")

        system_prompt = config.get_text(
            "correction_system_prompt",
            "Eres un profesor de idiomas amable y conciso. El usuario está aprendiendo y te dará una respuesta a una pregunta. Tu tarea es: \n1. Evaluar si la respuesta del usuario es correcta para la pregunta dada.\n2. Si es correcta, felicítale brevemente (ej: '¡Perfecto!', '¡Muy bien!').\n3. Si es incorrecta, corrígele de forma sencilla y directa, explicando el porqué del error en una sola frase.\nResponde siempre en español."
        )

        user_message = config.get_text(
            "correction_question_template",
            "La pregunta era: '{question}'. Mi respuesta fue: '{answer}'."
        ).format(question=prompt_question, answer=user_answer)

        try:
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=100
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(config.get_text("deepseek_api_error", "Error en la llamada a la API de DeepSeek: {error}").format(error=str(e)))
            return config.get_text("api_error", "Hubo un error al contactar con el servicio de IA.")