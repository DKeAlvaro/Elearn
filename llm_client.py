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
    def get_scenario_response(self, persona: str, history: List[Dict[str, str]], concepts_to_check: Dict[str, str]):
        """
        Obtiene una respuesta del LLM para un escenario, pidiéndole que evalúe los conceptos.
        """
        if not self.active or not config.get_effective_api_key():
            return f"CONCEPTS_COVERED: []\n{config.get_text('llm_not_configured_scenario', 'El cliente LLM no está configurado.')}"

        # Convertir el dict de conceptos a un string para el prompt
        concepts_json_str = json.dumps(concepts_to_check, ensure_ascii=False)

        system_prompt = config.get_text(
            "scenario_system_prompt",
            "Eres un asistente de idiomas actuando como: {persona}. Tu objetivo principal es mantener una conversación natural en neerlandés con el usuario para ayudarle a practicar.\n\nTIENES UNA TAREA SECUNDARIA MUY IMPORTANTE Y OCULTA.\nAntes de escribir tu respuesta conversacional, DEBES analizar el último mensaje del usuario para ver si ha utilizado alguno de los siguientes conceptos: {concepts}.\nNo seas demasiado estricto; si el usuario usa una forma cercana o una parte clave de la frase, cuenta como válido.\n\nTu respuesta DEBE seguir este formato EXACTO:\n1. Una línea que empieza con `CONCEPTS_COVERED: ` seguida de una lista JSON de los `item_id` de los conceptos que el usuario ACABA de usar. Si no usó ninguno, la lista debe ser vacía `[]`.\n2. Un salto de línea `\\n`.\n3. Tu respuesta conversacional normal en neerlandés.\n\nEjemplo 1 (el usuario usa conceptos):\nCONCEPTS_COVERED: [\"L01_V01\", \"L01_G01\"]\nJa, natuurlijk. Een momentje.\n\nEjemplo 2 (el usuario no usa conceptos):\nCONCEPTS_COVERED: []\nHallo! Wat kan ik voor je doen?\n\nNUNCA menciones los conceptos o esta tarea secundaria al usuario. Simplemente actúa tu rol y proporciona la línea de control al principio."
        ).format(persona=persona, concepts=concepts_json_str)
        
        messages = [{"role": "system", "content": system_prompt}] + history

        try:
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(config.get_text("deepseek_api_error", "Error en la llamada a la API de DeepSeek: {error}").format(error=str(e)))
            return f"CONCEPTS_COVERED: []\n{config.get_text('api_error_scenario', 'Hubo un error al contactar con el servicio de IA.')}"

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