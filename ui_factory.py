import flet as ft

def create_slide_content(slide_data: dict):
    """
    Crea un control de Flet (o una lista de ellos) basado en el tipo de diapositiva.
    """
    slide_type = slide_data.get('type')
    
    # --- NUEVO: Manejador para el escenario interactivo ---
    if slide_type == 'interactive_scenario':
        # +++ ADDED progress_text control +++
        progress_text = ft.Text(size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
        chat_messages = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        new_message = ft.TextField(
            hint_text="Escribe tu respuesta...", 
            expand=True,
            border_radius=20,
            border_color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            height=50,
            content_padding=15
        )
        send_button = ft.IconButton(icon=ft.Icons.SEND_ROUNDED, icon_color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_GREY_500)

        container = ft.Column(
            controls=[
                ft.Text(slide_data.get('title', 'Conversación'), size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"Tu objetivo: {slide_data.get('user_goal')}", size=16),
                progress_text,
                ft.Divider(),
                chat_messages,
                ft.Row(
                    controls=[new_message, send_button],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            expand=True,
            spacing=10
        )
        # +++ RETURN the new control +++
        return {
            "container": container, 
            "chat_messages": chat_messages, 
            "new_message": new_message, 
            "send_button": send_button,
            "progress_text": progress_text
        }

    if slide_type == 'llm_check':
        prompt_text = ft.Text(slide_data['prompt'], size=20, text_align=ft.TextAlign.CENTER)
        answer_field = ft.TextField(label="Tu respuesta...", width=300, text_align=ft.TextAlign.CENTER)
        check_button = ft.ElevatedButton("Comprobar con IA")
        result_text = ft.Text(value="", size=16, text_align=ft.TextAlign.CENTER, italic=True)
        
        container = ft.Column(
            controls=[prompt_text, answer_field, check_button, ft.Container(result_text, padding=10)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True
        )
        return {"container": container, "answer_field": answer_field, "check_button": check_button, "result_text": result_text}

    content_controls = []

    if slide_type == 'vocabulary':
        word, translation = list(slide_data['data'].items())[0]
        content_controls.extend([
            ft.Text(word, size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(translation, size=24, italic=True, text_align=ft.TextAlign.CENTER)
        ])
    
    elif slide_type == 'expression':
        phrase = slide_data['data']['phrase']
        meaning = slide_data['data']['meaning']
        content_controls.extend([
            ft.Text(f'"{phrase}"', size=32, text_align=ft.TextAlign.CENTER),
            ft.Text(meaning, size=20, italic=True, text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY)
        ])

    elif slide_type == 'grammar':
        content_controls.extend([
            ft.Text(slide_data['title'], size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(slide_data['explanation'], size=18, text_align=ft.TextAlign.CENTER)
        ])
        
    elif slide_type == 'tip':
         content_controls.extend([
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=ft.Colors.AMBER),
            ft.Text(slide_data['text'], size=18, italic=True, text_align=ft.TextAlign.CENTER)
        ])

    elif slide_type == 'practice_builder':
        content_controls.append(ft.Text(slide_data['task'], size=20))
        correct_phrase = " ".join(slide_data['structure'])
        content_controls.extend([
            ft.Text(correct_phrase, size=28, weight=ft.FontWeight.BOLD),
            ft.Text(slide_data['translation'], size=18, italic=True)
        ])
        
    elif slide_type == 'extra':
        content_controls.extend([
            ft.Text(slide_data['title'], size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(slide_data['content'], size=18, text_align=ft.TextAlign.CENTER)
        ])
        
    else:
        content_controls.append(ft.Text(f"Tipo de diapositiva desconocido: {slide_type}"))

    content_column = ft.Column(
        controls=content_controls,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        expand=True
    )
    return {"container": content_column}

# --- Componente reutilizable para los mensajes del chat ---
class ChatMessage(ft.Row):
    def __init__(self, message: str, is_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Icon(ft.Icons.PERSON if is_user else ft.Icons.ANDROID),
                bgcolor=ft.Colors.BLUE_GREY_100 if is_user else ft.Colors.TEAL_200,
            ),
            ft.Container(
                content=ft.Text(message, selectable=True),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK) if is_user else ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                expand=True,
            ),
        ]