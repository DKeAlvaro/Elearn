# views/premium_view.py
import flet as ft
from src.managers.billing_manager import billing_manager
import src.config as config


def PremiumView(page: ft.Page):
    """Premium unlock view for in-app purchase"""
    
    # State variables
    purchase_status = ft.Text("", size=14, color=ft.Colors.GREY_600)
    purchase_button = ft.ElevatedButton(
        text="Unlock Premium - €5.00",
        on_click=None,  # Will be set later
        disabled=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=32, vertical=16),
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
    )
    
    loading_indicator = ft.ProgressRing(width=20, height=20, visible=False)
    
    def on_purchase_result(success: bool, message: str):
        """Handle purchase result callback"""
        loading_indicator.visible = False
        purchase_button.disabled = False
        
        if success:
            purchase_status.value = "✅ Premium unlocked successfully!"
            purchase_status.color = ft.Colors.GREEN
            purchase_button.visible = False
            # Refresh the page to show unlocked content
            page.go("/")
        else:
            purchase_status.value = f"❌ {message}"
            purchase_status.color = ft.Colors.RED
        
        page.update()
    
    def on_connection_result(success: bool):
        """Handle billing connection result"""
        if success:
            purchase_status.value = "Ready to purchase"
            purchase_status.color = ft.Colors.GREEN
            purchase_button.disabled = False
        else:
            purchase_status.value = "Billing service unavailable"
            purchase_status.color = ft.Colors.RED
            purchase_button.disabled = True
        
        loading_indicator.visible = False
        page.update()
    
    def start_purchase(e):
        """Start the purchase process"""
        loading_indicator.visible = True
        purchase_button.disabled = True
        purchase_status.value = "Processing purchase..."
        purchase_status.color = ft.Colors.BLUE
        page.update()
        
        # Launch purchase flow
        success = billing_manager.launch_purchase_flow()
        if not success:
            loading_indicator.visible = False
            purchase_button.disabled = False
            purchase_status.value = "Failed to start purchase"
            purchase_status.color = ft.Colors.RED
            page.update()
    
    # Set the purchase button callback
    purchase_button.on_click = start_purchase
    
    def go_back(e):
        """Go back to home view"""
        page.go("/")
    
    # Initialize billing manager when view loads
    def initialize_billing():
        """Initialize billing manager"""
        loading_indicator.visible = True
        purchase_status.value = "Connecting to billing service..."
        purchase_status.color = ft.Colors.BLUE
        page.update()
        
        # Check if already premium
        if billing_manager.check_premium_status():
            purchase_status.value = "You already have premium access!"
            purchase_status.color = ft.Colors.GREEN
            purchase_button.visible = False
            loading_indicator.visible = False
            page.update()
            return
        
        # Initialize billing client
        billing_manager.initialize_billing_client(
            purchase_callback=on_purchase_result,
            connection_callback=on_connection_result
        )
    
    # Initialize billing when view is created
    initialize_billing()
    
    return ft.View(
        "/premium",
        controls=[
            CustomAppBar(
                title="Unlock Premium",
                page=page,
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=go_back
                )
            ),
            ft.Container(
                content=ft.Column([
                    # Premium features header
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.STAR,
                                size=64,
                                color=ft.Colors.AMBER
                            ),
                            ft.Text(
                                "Unlock All Content",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16
                        ),
                        padding=ft.padding.symmetric(vertical=32)
                    ),
                    
                    # Features list
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                                    ft.Text("Access to all lessons", size=16, expand=True)
                                ], spacing=12),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                                    ft.Text("No advertisements", size=16, expand=True)
                                ], spacing=12),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=24),
                                    ft.Text("Lifetime access", size=16, expand=True)
                                ], spacing=12)
                            ], spacing=16),
                            padding=24
                        ),
                        elevation=2,
                        margin=ft.margin.symmetric(vertical=16)
                    ),
                    
                    # Purchase section
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                loading_indicator,
                                purchase_status
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=12
                            ),
                            ft.Container(height=16),
                            purchase_button,
                            ft.Container(height=16),
                            ft.Text(
                                "One-time payment • Secure checkout via Google Play",
                                size=12,
                                color=ft.Colors.GREY_500,
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                        ),
                        padding=ft.padding.symmetric(vertical=24)
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
                ),
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                expand=True
            )
        ],
        padding=0,
        scroll=ft.ScrollMode.AUTO
    )