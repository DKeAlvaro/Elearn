# views/settings_view.py
import flet as ft
import src.config as config
from src.managers.settings_manager import SettingsManager
from src.app_state import AppState

from src.ui_components import CustomAppBar

def SettingsView(page: ft.Page, settings_manager: SettingsManager, app_state: AppState = None):
    api_key_field = ft.TextField(
        label=config.get_text("api_key_label", "DeepSeek API Key"),
        password=True,
        can_reveal_password=True,
        width=400,
        helper_text=config.get_text("api_key_helper", "Enter your DeepSeek API key to enable AI features"),
        value=config.get_user_api_key() or ""
    )
    
    status_message = ft.Text(
        value="",
        size=14,
        text_align=ft.TextAlign.CENTER
    )
    
    def save_api_key_click(e):
        settings_manager.save_api_key(api_key_field.value.strip(), status_message)
    
    def clear_api_key_click(e):
        settings_manager.clear_api_key(api_key_field, status_message)
    
    def go_back(e):
        page.go("/")
    

    
    save_button = ft.ElevatedButton(
        text=config.get_text("save", "Save"),
        on_click=save_api_key_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=12)
        )
    )
    
    clear_button = ft.OutlinedButton(
        text=config.get_text("clear", "Clear"),
        on_click=clear_api_key_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=12)
        )
    )
    
    info_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE),
                    ft.Text(
                        config.get_text("api_key_info_title", "About API Keys"),
                        size=16,
                        weight=ft.FontWeight.BOLD
                    )
                ]),
                ft.Text(
                    config.get_text(
                        "api_key_info_text", 
                        "You need a DeepSeek API key to use AI-powered features like exercise correction and interactive scenarios. Get your free API key at https://platform.deepseek.com"
                    ),
                    size=14,
                    color=ft.Colors.GREY_700
                )
            ], spacing=10),
            padding=20,
            border_radius=12
        ),
        elevation=1,
        margin=ft.margin.symmetric(vertical=16)
    )
    

    
    return ft.View(
        "/settings",
        controls=[
            CustomAppBar(
                title=config.get_text("settings", "Settings"),
                page=page,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_back
                )
            ),
            ft.Container(
                content=ft.Column([
                    info_card,
                    ft.Container(
                        content=ft.Column([
                            api_key_field,
                            ft.Container(height=10),
                            ft.Row([
                                save_button,
                                clear_button
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                            ft.Container(height=20),
                            status_message
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                expand=True
            )
        ],
        padding=0,
        scroll=ft.ScrollMode.AUTO
    )