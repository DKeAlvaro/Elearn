import flet as ft
import webbrowser
import urllib.parse
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from src.firebase_manager import FirebaseManager
from src.app_state import AppState

def LoginView(page: ft.Page, app_state: AppState):
    firebase_manager = FirebaseManager()
    
    # Status text for showing authentication progress
    status_text = ft.Text("", size=14, color=ft.Colors.BLUE_600)
    
    # Global variables for OAuth callback
    oauth_result = {"code": None, "error": None, "completed": False}
    
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # Parse the callback URL
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if 'code' in query_params:
                oauth_result["code"] = query_params['code'][0]
                oauth_result["completed"] = True
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html><body>
                        <h2>Authentication Successful!</h2>
                        <p>You can now close this window and return to the app.</p>
                        <script>window.close();</script>
                    </body></html>
                ''')
            else:
                oauth_result["error"] = query_params.get('error', ['Unknown error'])[0]
                oauth_result["completed"] = True
                
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html><body>
                        <h2>Authentication Failed</h2>
                        <p>Please close this window and try again.</p>
                    </body></html>
                ''')
        
        def log_message(self, format, *args):
            # Suppress server logs
            pass

    def google_sign_in_click(e):
        try:
            # Get Firebase config
            firebase_config = firebase_manager.get_firebase_config()
            google_client_id = os.getenv('GOOGLE_CLIENT_ID')
            google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            
            if not google_client_id or not google_client_secret or not firebase_config.get('apiKey'):
                status_text.value = "Please configure your Firebase and Google OAuth settings in .env file"
                status_text.color = ft.Colors.RED_600
                page.update()
                return
            
            status_text.value = "Starting Google authentication..."
            status_text.color = ft.Colors.BLUE_600
            page.update()
            
            # Reset OAuth result
            oauth_result["code"] = None
            oauth_result["error"] = None
            oauth_result["completed"] = False
            
            # Start callback server
            def start_callback_server():
                server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
                server.timeout = 60  # 1 minute timeout
                server.handle_request()  # Handle only one request
                server.server_close()
            
            # Start server in background thread
            server_thread = threading.Thread(target=start_callback_server, daemon=True)
            server_thread.start()
            
            # Create Google OAuth URL
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                'client_id': google_client_id,
                'redirect_uri': 'http://localhost:8080',
                'scope': 'openid email profile',
                'response_type': 'code',
                'access_type': 'offline',
                'prompt': 'consent'
            }
            
            full_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
            
            status_text.value = "Opening Google sign-in in your browser..."
            status_text.color = ft.Colors.BLUE_600
            page.update()
            
            # Open browser for authentication
            webbrowser.open(full_url)
            
            # Wait for OAuth callback
            def check_oauth_result():
                timeout = 60  # 60 seconds timeout
                start_time = time.time()
                
                while not oauth_result["completed"] and (time.time() - start_time) < timeout:
                    time.sleep(1)
                
                if oauth_result["completed"]:
                    if oauth_result["code"]:
                        # Exchange code for tokens
                        exchange_code_for_tokens(oauth_result["code"], google_client_id, google_client_secret)
                    else:
                        status_text.value = f"Authentication failed: {oauth_result['error']}"
                        status_text.color = ft.Colors.RED_600
                        page.update()
                else:
                    status_text.value = "Authentication timed out. Please try again."
                    status_text.color = ft.Colors.RED_600
                    page.update()
            
            # Start OAuth result checker in background thread
            oauth_thread = threading.Thread(target=check_oauth_result, daemon=True)
            oauth_thread.start()
            
        except Exception as e:
            status_text.value = f"Error: {str(e)}"
            status_text.color = ft.Colors.RED_600
            page.update()
    
    def exchange_code_for_tokens(code, client_id, client_secret):
        try:
            status_text.value = "Exchanging authorization code for tokens..."
            status_text.color = ft.Colors.BLUE_600
            page.update()
            
            # Exchange authorization code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:8080'
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()
            
            if 'access_token' in token_json:
                # Get user info from Google
                user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_json['access_token']}"
                user_response = requests.get(user_info_url)
                user_data = user_response.json()
                
                if user_response.status_code == 200:
                    # Create user object
                    class GoogleUser:
                        def __init__(self, user_data):
                            self.uid = user_data.get('id')
                            self.email = user_data.get('email')
                            self.display_name = user_data.get('name')
                            self.picture = user_data.get('picture')
                            self.provider = "google.com"
                    
                    app_state.user = GoogleUser(user_data)
                    
                    status_text.value = f"Welcome {user_data.get('name', 'User')}! Redirecting..."
                    status_text.color = ft.Colors.GREEN_600
                    page.update()
                    
                    # Navigate to home after a short delay
                    time.sleep(1)
                    page.go("/")
                else:
                    status_text.value = "Failed to get user information from Google"
                    status_text.color = ft.Colors.RED_600
                    page.update()
            else:
                status_text.value = f"Token exchange failed: {token_json.get('error', 'Unknown error')}"
                status_text.color = ft.Colors.RED_600
                page.update()
                
        except Exception as e:
            status_text.value = f"Token exchange error: {str(e)}"
            status_text.color = ft.Colors.RED_600
            page.update()
    
    def simulate_login_click(e):
        """Temporary function to simulate successful login for testing"""
        try:
            status_text.value = "Simulating login with Firebase connection..."
            status_text.color = ft.Colors.BLUE_600
            page.update()
            
            # Test Firebase connection
            firebase_config = firebase_manager.get_firebase_config()
            if firebase_config:
                status_text.value = "Firebase connected successfully! Creating test user..."
                status_text.color = ft.Colors.GREEN_600
                page.update()
                
                # Create a mock user that simulates a real Firebase user
                class MockUser:
                    def __init__(self):
                        self.uid = "test_user_123"
                        self.email = "test@example.com"
                        self.display_name = "Test User"
                        self.provider = "google.com"
                
                app_state.user = MockUser()
                
                status_text.value = "Login successful! Redirecting to home..."
                status_text.color = ft.Colors.GREEN_600
                page.update()
                
                # Navigate to home
                page.go("/")
            else:
                status_text.value = "Firebase configuration error"
                status_text.color = ft.Colors.RED_600
                page.update()
                
        except Exception as e:
            status_text.value = f"Login simulation error: {str(e)}"
            status_text.color = ft.Colors.RED_600
            page.update()

    return ft.View(
        "/login",
        controls=[
            ft.Column(
                [
                    # App logo
                    ft.Container(
                        content=ft.Image(
                            src="assets/logo.svg",
                            width=100,
                            height=100,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(bottom=20)
                    ),
                    
                    # Welcome text
                    ft.Text(
                        "Welcome to LLMers",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    ft.Text(
                        "Sign in with your Google account to continue",
                        size=16,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    ft.Container(height=30),
                    
                    # Google Sign In Button
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOGIN, size=20),
                                    ft.Text("Continue with Google", size=16, weight=ft.FontWeight.W_500)
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10
                            ),
                            on_click=google_sign_in_click,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLUE_600,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            width=280,
                            height=50
                        ),
                        alignment=ft.alignment.center
                    ),
                    
                    ft.Container(height=20),
                    
                    # Status text
                    status_text,
                    
                    ft.Container(height=20),
                    
                    # Temporary test button (remove in production)
                    ft.Container(
                        content=ft.TextButton(
                            "Skip Login (Test Mode)",
                            on_click=simulate_login_click,
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_600
                            )
                        ),
                        alignment=ft.alignment.center
                    ),
                    
                    ft.Container(height=40),
                    
                    # Terms and privacy
                    ft.Text(
                        "By continuing, you agree to our Terms of Service and Privacy Policy",
                        size=12,
                        color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=ft.padding.symmetric(horizontal=40, vertical=20)
    )