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
    
    def go_to_logout(e):
        page.go("/logout")
    
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
    
    # User info and logout section
    user_info_card = None
    if app_state and app_state.user:
        user_name = "User"
        user_email = ""
        
        if hasattr(app_state.user, 'display_name') and app_state.user.display_name:
            user_name = app_state.user.display_name
        if hasattr(app_state.user, 'email') and app_state.user.email:
            user_email = app_state.user.email
            if not user_name or user_name == "User":
                user_name = user_email.split('@')[0]
        
        user_info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=ft.Colors.GREEN, size=24),
                        ft.Text(
                            config.get_text("account_info", "Account Information"),
                            size=16,
                            weight=ft.FontWeight.BOLD
                        )
                    ]),
                    ft.Container(height=10),
                    ft.Text(
                        f"Name: {user_name}",
                        size=14,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Text(
                        f"Email: {user_email}",
                        size=14,
                        color=ft.Colors.GREY_700
                    ) if user_email else ft.Container(),
                    ft.Container(height=15),
                    ft.FilledButton(
                        text=config.get_text("logout", "Logout"),
                        on_click=go_to_logout,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=12),
                            padding=ft.padding.symmetric(horizontal=24, vertical=12)
                        ),
                        icon=ft.Icons.LOGOUT
                    )
                ], spacing=5),
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
                    user_info_card if user_info_card else ft.Container(),
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