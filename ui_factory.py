# ui_factory.py
import flet as ft
import config
from ui_components import ChatMessage

def create_slide_content(slide_data: dict):
    """
    Crea un control de Flet (o una lista de ellos) basado en el tipo de diapositiva.
    """
    slide_type = slide_data.get('type')
    
    # --- NUEVO: Manejador para el escenario interactivo ---
    if slide_type == 'interactive_scenario':
        # +++ ADDED progress_container for styled objectives +++
        progress_container = ft.Column(spacing=8)
        chat_messages = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        new_message = ft.TextField(label=config.get_text("type_message", "Escribe tu mensaje..."), expand=True)
        send_button = ft.ElevatedButton(config.get_text("send_message", "Enviar"))
        restart_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip=config.get_text("restart_scenario", "Reiniciar escenario"),
            icon_size=20
        )
        # Create a scrollable container that includes title, objectives, progress, and messages
        scrollable_content = ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Text(slide_data.get('title', 'Conversación'), size=24, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(bottom=10)
                ),
                ft.Container(
                    content=ft.Text(f"{slide_data.get('setting')}", size=16),
                    padding=ft.padding.only(bottom=10)
                ),
                ft.Container(
                    content=progress_container,
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY),
                    border_radius=8
                ),
                ft.Divider(),
            ],
            expand=True,
            spacing=10,
            auto_scroll=True
        )
        
        container = ft.Column(
            controls=[
                scrollable_content,
                ft.Row(
                    controls=[new_message, send_button, restart_button],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            expand=True,
            spacing=10
        )
        # +++ RETURN the new control +++
        return {
            "container": container, 
            "scrollable_content": scrollable_content, 
            "new_message": new_message, 
            "send_button": send_button,
            "restart_button": restart_button,
            "progress_container": progress_container
        }

    if slide_type == 'llm_check':
        prompt_text = ft.Text(slide_data['chatbot_message'], size=20, text_align=ft.TextAlign.CENTER)
        answer_field = ft.TextField(label=config.get_text("your_answer", "Tu respuesta..."), width=300, text_align=ft.TextAlign.CENTER)
        check_button = ft.ElevatedButton(config.get_text("check_with_ai", "Comprobar con IA"))
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
            ft.Text(f'{phrase}', size=32, text_align=ft.TextAlign.CENTER),
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
        
    elif slide_type == 'pronunciation':
        word = slide_data['data']['word']
        phonetic = slide_data['data']['phonetic']
        tip = slide_data['data']['tip']
        content_controls.extend([
            ft.Text(word, size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(f"[{phonetic}]", size=24, italic=True, text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_700),
            ft.Icon(ft.Icons.VOLUME_UP, size=30, color=ft.Colors.BLUE_500),
            ft.Text(tip, size=16, text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY_700)
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
