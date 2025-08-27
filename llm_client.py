# llm_client.py

import config
from openai import OpenAI

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