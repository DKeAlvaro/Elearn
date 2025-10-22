import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseManager:
    def __init__(self):
        try:
            # Initialize Firebase Admin SDK
            if not firebase_admin._apps:
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
                if service_account_path and os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    # Alternative: use individual environment variables
                    service_account_info = {
                        "type": "service_account",
                        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    }
                    cred = credentials.Certificate(service_account_info)
                
                firebase_admin.initialize_app(cred)
                print("Firebase app initialized successfully.")
        except Exception as e:
            print(f"Error initializing Firebase app: {e}")

    def verify_id_token(self, id_token):
        """Verify Firebase ID token from client-side authentication"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            user = auth.get_user(uid)
            return user
        except Exception as e:
            print(f"Error verifying ID token: {e}")
            return None

    def get_user_by_email(self, email):
        """Get user by email address"""
        try:
            user = auth.get_user_by_email(email)
            return user
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def create_custom_token(self, uid):
        """Create a custom token for a user"""
        try:
            custom_token = auth.create_custom_token(uid)
            return custom_token
        except Exception as e:
            print(f"Error creating custom token: {e}")
            return None

    def create_or_update_user(self, google_user_data):
        """Create or update a user in Firebase Authentication using Google OAuth data"""
        try:
            email = google_user_data.get('email')
            google_uid = google_user_data.get('id')
            name = google_user_data.get('name')
            picture = google_user_data.get('picture')
            
            if not email or not google_uid:
                raise ValueError("Missing required user data (email or Google UID)")
            
            # Try to get existing user by email
            try:
                existing_user = auth.get_user_by_email(email)
                # Update existing user
                auth.update_user(
                    existing_user.uid,
                    display_name=name,
                    photo_url=picture
                )
                print(f"Updated existing user: {email}")
                return existing_user
            except auth.UserNotFoundError:
                # Create new user
                user_record = auth.create_user(
                    uid=f"google_{google_uid}",  # Use Google UID with prefix
                    email=email,
                    display_name=name,
                    photo_url=picture,
                    email_verified=True  # Google emails are pre-verified
                )
                print(f"Created new user: {email}")
                return user_record
                
        except Exception as e:
            print(f"Error creating/updating user: {e}")
            return None

    def get_firebase_config(self):
        """Get Firebase configuration for client-side initialization"""
        return {
            "apiKey": os.getenv('FIREBASE_API_KEY'),
            "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "projectId": os.getenv('FIREBASE_PROJECT_ID'),
            "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            "appId": os.getenv('FIREBASE_APP_ID')
        }