# ui_components.py
import flet as ft
import config

# --- Componentes de Mensajes ---

class ChatMessage(ft.Row):
    """Un componente reutilizable para mostrar un mensaje en el chat."""
    def __init__(self, message_control: ft.Control, is_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        message_bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.BLACK) if is_user else ft.Colors.with_opacity(0.05, ft.Colors.BLACK)

        avatar_content = ft.Icon(ft.Icons.PERSON) if is_user else ft.Image(src="assets/logo.svg", width=24, height=24, fit=ft.ImageFit.CONTAIN)
        avatar_color = ft.Colors.BLUE_GREY_100 if is_user else ft.Colors.TEAL_200

        self.controls = [
            ft.CircleAvatar(content=avatar_content, bgcolor=avatar_color),
            ft.Container(
                content=message_control,
                padding=10,
                border_radius=10,
                bgcolor=message_bgcolor,
                expand=True,
            ),
        ]

class LoadingMessage(ft.Row):
    """Muestra un indicador de carga para simular la respuesta del asistente."""
    def __init__(self):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Image(src="assets/logo.svg", width=24, height=24, fit=ft.ImageFit.CONTAIN),
                bgcolor=ft.Colors.TEAL_200,
            ),
            ft.Container(
                content=ft.ProgressRing(width=20, height=20, stroke_width=2),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            ),
        ]

# --- Componentes de Diapositivas ---

class BaseSlide(ft.Column):
    """Clase base para todas las diapositivas, centrando el contenido."""
    def __init__(self, controls: list, **kwargs):
        super().__init__(
            controls=controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True,
            **kwargs
        )

class VocabularySlide(BaseSlide):
    """Diapositiva para mostrar una palabra de vocabulario y su traducción."""
    def __init__(self, slide_data: dict):
        word, translation = list(slide_data['data'].items())[0]
        controls = [
            ft.Text(word, size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(translation, size=24, italic=True, text_align=ft.TextAlign.CENTER)
        ]
        super().__init__(controls)

class ExpressionSlide(BaseSlide):
    """Diapositiva para mostrar una expresión y su significado."""
    def __init__(self, slide_data: dict):
        phrase = slide_data['data']['phrase']
        meaning = slide_data['data']['meaning']
        controls = [
            ft.Text(f'"{phrase}"', size=32, text_align=ft.TextAlign.CENTER),
            ft.Text(meaning, size=20, italic=True, text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY)
        ]
        super().__init__(controls)

class GrammarSlide(BaseSlide):
    """Diapositiva para explicar una regla gramatical."""
    def __init__(self, slide_data: dict):
        controls = [
            ft.Text(slide_data['title'], size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(slide_data['explanation'], size=18, text_align=ft.TextAlign.CENTER)
        ]
        super().__init__(controls)

class TipSlide(BaseSlide):
    """Diapositiva para mostrar un consejo o tip."""
    def __init__(self, slide_data: dict):
        controls = [
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=ft.Colors.AMBER),
            ft.Text(slide_data['text'], size=18, italic=True, text_align=ft.TextAlign.CENTER)
        ]
        super().__init__(controls)

class PracticeBuilderSlide(BaseSlide):
    """Diapositiva para practicar la construcción de frases."""
    def __init__(self, slide_data: dict):
        correct_phrase = " ".join(slide_data['structure'])
        controls = [
            ft.Text(slide_data['task'], size=20),
            ft.Text(correct_phrase, size=28, weight=ft.FontWeight.BOLD),
            ft.Text(slide_data['translation'], size=18, italic=True)
        ]
        super().__init__(controls)

class ExtraSlide(BaseSlide):
    """Diapositiva para contenido extra."""
    def __init__(self, slide_data: dict):
        controls = [
            ft.Text(slide_data['title'], size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(slide_data['content'], size=18, text_align=ft.TextAlign.CENTER)
        ]
        super().__init__(controls)

class PronunciationSlide(BaseSlide):
    """Diapositiva para practicar la pronunciación."""
    def __init__(self, slide_data: dict):
        word = slide_data['data']['word']
        phonetic = slide_data['data']['phonetic']
        tip = slide_data['data']['tip']
        controls = [
            ft.Text(word, size=50, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(f"[{phonetic}]", size=24, italic=True, text_align=ft.TextAlign.CENTER, color=ft.Colors.BLUE_700),
            ft.Icon(ft.Icons.VOLUME_UP, size=30, color=ft.Colors.BLUE_500),
            ft.Text(tip, size=16, text_align=ft.TextAlign.CENTER, color=ft.Colors.GREY_700)
        ]
        super().__init__(controls)

class CustomAppBar(ft.AppBar):
    """AppBar reutilizable con el logo y un título personalizable."""
    def __init__(self, title: str, page: ft.Page, leading: ft.Control = None, actions: list = None):
        super().__init__(
            title=ft.Row([
                ft.Image(src="assets/logo.svg", width=28, height=28, fit=ft.ImageFit.CONTAIN),
                ft.Container(width=10),
                ft.Text(title, size=20, weight=ft.FontWeight.W_600)
            ], alignment=ft.MainAxisAlignment.CENTER),
            center_title=True,
            bgcolor=ft.Colors.TRANSPARENT,
            elevation=0,
            leading=leading,
            actions=actions
        )
        self.page = page

class InteractiveScenarioSlide(ft.Column):
    """Diapositiva para un escenario de conversación interactivo."""
    def __init__(self, slide_data: dict):
        self.progress_container = ft.Column(spacing=8)
        self.scrollable_content = ft.ListView(
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
                    content=self.progress_container,
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
        self.new_message = ft.TextField(label=config.get_text("type_message", "Escribe tu mensaje..."), expand=True)
        self.send_button = ft.ElevatedButton(config.get_text("send_message", "Enviar"))
        self.restart_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip=config.get_text("restart_scenario", "Reiniciar escenario"),
            icon_size=20
        )
        
        super().__init__(
            controls=[
                self.scrollable_content,
                ft.Row(
                    controls=[self.new_message, self.send_button, self.restart_button],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            expand=True,
            spacing=10
        )

class LLMCheckSlide(ft.Column):
    """Diapositiva para que el LLM verifique la entrada del usuario."""
    def __init__(self, slide_data: dict):
        self.prompt_text = ft.Text(slide_data['prompt'], size=20, text_align=ft.TextAlign.CENTER)
        self.answer_field = ft.TextField(label=config.get_text("your_answer", "Tu respuesta..."), width=300, text_align=ft.TextAlign.CENTER)
        self.check_button = ft.ElevatedButton(config.get_text("check_with_ai", "Comprobar con IA"))
        self.result_text = ft.Text(value="", size=16, text_align=ft.TextAlign.CENTER, italic=True)
        
        super().__init__(
            controls=[
                self.prompt_text,
                self.answer_field,
                self.check_button,
                ft.Container(self.result_text, padding=10)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            expand=True
        )

# --- Fábrica de Diapositivas ---

def create_slide_content(slide_data: dict) -> ft.Control:
    """Crea el control de Flet adecuado basado en el tipo de diapositiva."""
    slide_type = slide_data.get('type')
    
    slide_map = {
        'vocabulary': VocabularySlide,
        'expression': ExpressionSlide,
        'grammar': GrammarSlide,
        'tip': TipSlide,
        'practice_builder': PracticeBuilderSlide,
        'extra': ExtraSlide,
        'pronunciation': PronunciationSlide,
        'interactive_scenario': InteractiveScenarioSlide,
        'llm_check': LLMCheckSlide,
    }
    
    slide_class = slide_map.get(slide_type)
    
    if slide_class:
        return slide_class(slide_data)
    else:
        return BaseSlide([ft.Text(f"Tipo de diapositiva desconocido: {slide_type}")])
