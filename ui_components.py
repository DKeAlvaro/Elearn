# ui_components.py
import flet as ft

class ChatMessage(ft.Row):
    """
    Un componente reutilizable para mostrar un mensaje en el chat.
    Ahora acepta un control de Flet como contenido del mensaje para permitir actualizaciones dinámicas.
    """
    def __init__(self, message_control: ft.Control, is_user: bool):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        message_bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.BLACK) if is_user else ft.Colors.with_opacity(0.05, ft.Colors.BLACK)

        # Use different avatars for user vs AI assistant
        if is_user:
            avatar_content = ft.Icon(ft.Icons.PERSON)
            avatar_color = ft.Colors.BLUE_GREY_100
        else:
            # Use logo for AI assistant
            avatar_content = ft.Image(
                src="assets/logo.svg",
                width=24,
                height=24,
                fit=ft.ImageFit.CONTAIN
            )
            avatar_color = ft.Colors.TEAL_200

        self.controls = [
            ft.CircleAvatar(
                content=avatar_content,
                bgcolor=avatar_color,
            ),
            ft.Container(
                content=message_control,
                padding=10,
                border_radius=10,
                bgcolor=message_bgcolor,
                expand=True,
            ),
        ]

class LoadingMessage(ft.Row):
    """
    Un componente que muestra un avatar y un indicador de progreso,
    simulando que el asistente de IA está "pensando" o "escribiendo".
    """
    def __init__(self):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Image(
                    src="assets/logo.svg",
                    width=24,
                    height=24,
                    fit=ft.ImageFit.CONTAIN
                ),
                bgcolor=ft.Colors.TEAL_200,
            ),
            ft.Container(
                content=ft.ProgressRing(width=20, height=20, stroke_width=2),
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            ),
        ]