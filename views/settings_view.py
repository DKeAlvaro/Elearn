# views/settings_view.py
import flet as ft
import config
import json
import os

def SettingsView(page: ft.Page, llm_client=None):
    # Create input field for API key
    api_key_field = ft.TextField(
        label=config.get_text("api_key_label", "DeepSeek API Key"),
        password=True,
        can_reveal_password=True,
        width=400,
        helper_text=config.get_text("api_key_helper", "Enter your DeepSeek API key to enable AI features"),
        value=config.get_user_api_key() or ""
    )
    
    # Status message
    status_message = ft.Text(
        value="",
        size=14,
        text_align=ft.TextAlign.CENTER
    )
    
    def save_api_key(e):
        """Save the API key to user settings"""
        api_key = api_key_field.value.strip()
        
        if not api_key:
            status_message.value = config.get_text("api_key_empty_error", "Please enter an API key")
            status_message.color = ft.Colors.RED
        else:
            try:
                config.save_user_api_key(api_key)
                status_message.value = config.get_text("api_key_saved", "API key saved successfully!")
                status_message.color = ft.Colors.GREEN
                
                # Update the global API key
                config.update_runtime_api_key(api_key)
                
                # Update the LLM client with the new API key
                if llm_client:
                    llm_client.update_api_key()
                
            except Exception as ex:
                status_message.value = config.get_text("api_key_save_error", "Error saving API key: {error}").format(error=str(ex))
                status_message.color = ft.Colors.RED
        
        page.update()
    
    def clear_api_key(e):
        """Clear the saved API key"""
        try:
            config.clear_user_api_key()
            api_key_field.value = ""
            status_message.value = config.get_text("api_key_cleared", "API key cleared successfully!")
            status_message.color = ft.Colors.ORANGE
            
            # Reset to default API key
            config.update_runtime_api_key(None)
            
            # Update the LLM client
            if llm_client:
                llm_client.update_api_key()
            
        except Exception as ex:
            status_message.value = config.get_text("api_key_clear_error", "Error clearing API key: {error}").format(error=str(ex))
            status_message.color = ft.Colors.RED
        
        page.update()
    
    def go_back(e):
        """Navigate back to home"""
        page.go("/")
    
    # Save and Clear buttons
    save_button = ft.ElevatedButton(
        text=config.get_text("save", "Save"),
        on_click=save_api_key,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=12)
        )
    )
    
    clear_button = ft.OutlinedButton(
        text=config.get_text("clear", "Clear"),
        on_click=clear_api_key,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=24, vertical=12)
        )
    )
    
    # Information card
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
            ft.AppBar(
                title=ft.Row([
                    ft.Image(
                        src="assets/logo.svg",
                        width=28,
                        height=28,
                        fit=ft.ImageFit.CONTAIN
                    ),
                    ft.Container(width=10),
                    ft.Text(
                        config.get_text("settings", "Settings"),
                        size=20,
                        weight=ft.FontWeight.W_600
                    )
                ], alignment=ft.MainAxisAlignment.CENTER),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_back
                ),
                center_title=True,
                bgcolor=ft.Colors.TRANSPARENT,
                elevation=0
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