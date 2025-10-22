# views/logout_view.py
import flet as ft
import src.config as config
from src.app_state import AppState
from src.ui_components import CustomAppBar

def LogoutView(page: ft.Page, app_state: AppState):
    """Logout view that handles user logout and confirmation"""
    
    def confirm_logout(e):
        """Handle logout confirmation"""
        try:
            # Use the app_state logout method to properly clear sessions
            app_state.logout_user()
            
            # Navigate to login page
            page.go("/login")
            
        except Exception as ex:
            # Handle any logout errors
            error_text.value = f"Error during logout: {str(ex)}"
            error_text.color = ft.Colors.RED_600
            page.update()
    
    def cancel_logout(e):
        """Cancel logout and return to home"""
        page.go("/")
    
    # Error message text
    error_text = ft.Text("", size=14, color=ft.Colors.RED_600)
    
    # Get user display name for personalized message
    user_name = "User"
    if app_state.user and hasattr(app_state.user, 'display_name') and app_state.user.display_name:
        user_name = app_state.user.display_name
    elif app_state.user and hasattr(app_state.user, 'email') and app_state.user.email:
        user_name = app_state.user.email.split('@')[0]
    
    return ft.View(
        "/logout",
        controls=[
            CustomAppBar(
                title=config.get_text("logout", "Logout"),
                page=page,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip=config.get_text("back", "Back"),
                    on_click=cancel_logout
                )
            ),
            ft.Container(
                content=ft.Column([
                    ft.Container(height=40),
                    
                    # Logout icon
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.LOGOUT,
                            size=80,
                            color=ft.Colors.BLUE_600
                        ),
                        alignment=ft.alignment.center
                    ),
                    
                    ft.Container(height=30),
                    
                    # Logout confirmation message
                    ft.Text(
                        f"Goodbye, {user_name}!",
                        size=24,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.BLUE_700
                    ),
                    
                    ft.Container(height=10),
                    
                    ft.Text(
                        config.get_text("logout_confirmation", "Are you sure you want to log out?"),
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_600
                    ),
                    
                    ft.Container(height=40),
                    
                    # Action buttons
                    ft.Row([
                        ft.OutlinedButton(
                            text=config.get_text("cancel", "Cancel"),
                            on_click=cancel_logout,
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE_600,
                                side=ft.BorderSide(width=2, color=ft.Colors.BLUE_600),
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500)
                            ),
                            width=120
                        ),
                        
                        ft.FilledButton(
                            text=config.get_text("logout", "Logout"),
                            on_click=confirm_logout,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_500)
                            ),
                            width=120
                        )
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=20),
                    
                    ft.Container(height=20),
                    
                    # Error message
                    error_text,
                    
                    ft.Container(height=40),
                    
                    # Additional info
                    ft.Text(
                        config.get_text("logout_info", "You can always log back in anytime."),
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_500,
                        italic=True
                    )
                    
                ], 
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0),
                padding=ft.padding.symmetric(horizontal=40, vertical=20),
                expand=True
            )
        ],
        padding=0,
        scroll=ft.ScrollMode.AUTO
    )