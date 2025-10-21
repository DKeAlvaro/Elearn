# utils/typing_simulator.py
import flet as ft
import asyncio

async def simulate_typing(text_control: ft.Text, full_text: str, page: ft.Page):
    """
    Simula el efecto de escritura letra por letra en un control de texto de Flet.
    """
    text_control.value = ""
    # Añade un carácter a la vez para el efecto de escritura
    for char in full_text:
        text_control.value += char
        # Actualiza la página para mostrar el nuevo carácter (sin await)
        page.update() 
        # Una pequeña pausa para que el efecto sea visible y no demasiado rápido
        await asyncio.sleep(0.02)