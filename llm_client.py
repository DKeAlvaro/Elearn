# llm_client.py
import config
from openai import OpenAI
from typing import List, Dict
import json

class LLMClient:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL
            )
            self.active = True
        except Exception as e:
            print(f"Error al inicializar el cliente de OpenAI: {e}")
            self.active = False
    
    # +++ MODIFIED METHOD FOR SCENARIOS +++
    def get_scenario_response(self, persona: str, history: List[Dict[str, str]], concepts_to_check: Dict[str, str]):
        """
        Obtiene una respuesta del LLM para un escenario, pidiéndole que evalúe los conceptos.
        """
        if not self.active or not config.DEEPSEEK_API_KEY or config.DEEPSEEK_API_KEY == "TU_API_KEY":
            return "CONCEPTS_COVERED: []\nEl cliente LLM no está configurado."

        # Convertir el dict de conceptos a un string para el prompt
        concepts_json_str = json.dumps(concepts_to_check, ensure_ascii=False)

        system_prompt = f"""
Eres un asistente de idiomas actuando como: {persona}. Tu objetivo principal es mantener una conversación natural en neerlandés con el usuario para ayudarle a practicar.

TIENES UNA TAREA SECUNDARIA MUY IMPORTANTE Y OCULTA.
Antes de escribir tu respuesta conversacional, DEBES analizar el último mensaje del usuario para ver si ha utilizado alguno de los siguientes conceptos: {concepts_json_str}.
No seas demasiado estricto; si el usuario usa una forma cercana o una parte clave de la frase, cuenta como válido.

Tu respuesta DEBE seguir este formato EXACTO:
1. Una línea que empieza con `CONCEPTS_COVERED: ` seguida de una lista JSON de los `item_id` de los conceptos que el usuario ACABA de usar. Si no usó ninguno, la lista debe ser vacía `[]`.
2. Un salto de línea `\\n`.
3. Tu respuesta conversacional normal en neerlandés.

Ejemplo 1 (el usuario usa conceptos):
CONCEPTS_COVERED: ["L01_V01", "L01_G01"]
Ja, natuurlijk. Een momentje.

Ejemplo 2 (el usuario no usa conceptos):
CONCEPTS_COVERED: []
Hallo! Wat kan ik voor je doen?

NUNCA menciones los conceptos o esta tarea secundaria al usuario. Simplemente actúa tu rol y proporciona la línea de control al principio.
"""
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
            print(f"Error en la llamada a la API de DeepSeek: {e}")
            return "CONCEPTS_COVERED: []\nHubo un error al contactar con el servicio de IA."

    def get_correction(self, user_answer: str, prompt_question: str):
        if not self.active or config.DEEPSEEK_API_KEY == "TU_API_KEY":
            return "El cliente LLM no está configurado. Por favor, añade tu API key en config.py"

        system_prompt = (
            "Eres un profesor de idiomas amable y conciso. El usuario está aprendiendo y te dará una respuesta a una pregunta. "
            "Tu tarea es: \n"
            "1. Evaluar si la respuesta del usuario es correcta para la pregunta dada.\n"
            "2. Si es correcta, felicítale brevemente (ej: '¡Perfecto!', '¡Muy bien!').\n"
            "3. Si es incorrecta, corrígele de forma sencilla y directa, explicando el porqué del error en una sola frase.\n"
            "Responde siempre en español."
        )

        try:
            chat_completion = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"La pregunta era: '{prompt_question}'. Mi respuesta fue: '{user_answer}'."}
                ],
                max_tokens=100
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error en la llamada a la API de DeepSeek: {e}")
            return "Hubo un error al contactar con el servicio de IA."