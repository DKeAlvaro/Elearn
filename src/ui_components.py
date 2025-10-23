# ui_components.py
import flet as ft
import src.config as config
import threading
import time
from src.utils.network_utils import check_internet_connection

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
            ft.Text(f'{phrase}', size=32, text_align=ft.TextAlign.CENTER),
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

class AppLogo(ft.Image):
    """A reusable component for the app logo."""
    def __init__(self, width=150, height=150):
        super().__init__(
            src="assets/logo.svg",
            width=width,
            height=height,
            fit=ft.ImageFit.CONTAIN,
        )

class Title(ft.Text):
    """A reusable component for titles."""
    def __init__(self, value: str, size: int = 28, weight: ft.FontWeight = ft.FontWeight.BOLD, font_family: str = "Poppins"):
        super().__init__(
            value=value,
            size=size,
            weight=weight,
            font_family=font_family,
        )

class Subtitle(ft.Text):
    """A reusable component for subtitles."""
    def __init__(self, value: str, size: int = 16, weight: ft.FontWeight = ft.FontWeight.W_400, color: str = ft.Colors.GREY_600, text_align: ft.TextAlign = ft.TextAlign.CENTER, font_family: str = "Inter"):
        super().__init__(
            value=value,
            size=size,
            weight=weight,
            color=color,
            text_align=text_align,
            font_family=font_family,
        )

class PrimaryButton(ft.FilledButton):
    """A reusable component for primary buttons."""
    def __init__(self, text: str, on_click: callable, width: int = 220):
        super().__init__(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=32, vertical=16),
            ),
            width=width,
        )

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
                ft.Container(
                    content=ft.Text(
                        title, 
                        size=20, 
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                        overflow=ft.TextOverflow.VISIBLE,
                        no_wrap=False
                    ),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            center_title=True,
            bgcolor=ft.Colors.TRANSPARENT,
            surface_tint_color=ft.Colors.TRANSPARENT,
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
        self.new_message = ft.TextField(label=config.get_text("type_message", "Type your message..."), expand=True)
        self.send_button = ft.ElevatedButton(config.get_text("send_message", "Send"))
        self.restart_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip=config.get_text("restart_scenario", "Restart scenario"),
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
            spacing=2
        )

class LLMCheckSlide(ft.Column):
    """Diapositiva para que el LLM verifique la entrada del usuario."""
    def __init__(self, slide_data: dict):
        self.prompt_text = ft.Text(slide_data['chatbot_message'], size=20, text_align=ft.TextAlign.CENTER)
        self.answer_field = ft.TextField(label=config.get_text("your_answer", "Your answer..."), width=300, text_align=ft.TextAlign.CENTER)
        self.check_button = ft.ElevatedButton(config.get_text("check_with_ai", "Check with AI"))
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


# --- Network Status Component ---

class NetworkStatusComponent:
    """Component that displays network connectivity status with frequent updates"""
    
    def __init__(self, page: ft.Page, update_interval: int = 5):
        self.page = page
        self.update_interval = update_interval
        self.is_online = True
        self.is_running = False
        
        # Create the icon button
        self.icon_button = ft.IconButton(
            icon=ft.Icons.WIFI,
            icon_color=ft.Colors.GREEN,
            tooltip="Online",
            disabled=True  # Make it non-clickable, just an indicator
        )
        
        # Start the monitoring thread
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start the background thread to monitor network status"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_network, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the background monitoring"""
        self.is_running = False
    
    def _monitor_network(self):
        """Background thread function to check network status periodically"""
        while self.is_running:
            try:
                # Check internet connectivity
                current_status = check_internet_connection()
                
                # Update UI if status changed
                if current_status != self.is_online:
                    self.is_online = current_status
                    self._update_icon()
                
                # Wait for the specified interval
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error checking network status: {e}")
                time.sleep(self.update_interval)
    
    def _update_icon(self):
        """Update the icon based on current network status"""
        try:
            if self.is_online:
                self.icon_button.icon = ft.Icons.WIFI
                self.icon_button.icon_color = ft.Colors.GREEN
                self.icon_button.tooltip = "Online"
            else:
                self.icon_button.icon = ft.Icons.WIFI_OFF
                self.icon_button.icon_color = ft.Colors.RED
                self.icon_button.tooltip = "Offline"
            
            # Update the page
            if self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error updating network status icon: {e}")
    
    def get_component(self):
        """Return the icon button component"""
        return self.icon_button
