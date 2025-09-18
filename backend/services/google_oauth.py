import json
import requests as http_requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from config import settings
from models_init import User
from services.user import UserService
from services.auth import AuthService


class GoogleOAuthService:
    """Service for handling Google OAuth2 authentication"""
    
    @staticmethod
    def get_google_flow() -> Flow:
        """Create and configure Google OAuth2 flow"""
        # Disable HTTPS requirement for local development
        import os
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }
        
        # Use full scope URLs as Google now requires
        scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        
        flow = Flow.from_client_config(
            client_config,
            scopes=scopes,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        return flow
    
    @staticmethod
    def get_authorization_url(jwt_state: str = None) -> str:
        """Get Google OAuth2 authorization URL with JWT state"""
        from urllib.parse import urlencode
        
        # Build OAuth URL manually to control the state parameter
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        params = {
            "response_type": "code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile",
            "access_type": "offline",
            "include_granted_scopes": "true",
            "state": jwt_state  # Our JWT state
        }
        
        authorization_url = f"{base_url}?{urlencode(params)}"
        return authorization_url
    
    @staticmethod
    def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            # Verify the token with clock skew tolerance
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=60  # Allow 60 seconds clock skew
            )
            
            # Check if token is from Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return idinfo
            
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
    
    @staticmethod
    def create_oauth_state() -> str:
        """Create JWT state token for OAuth security"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        
        state_data = {
            "timestamp": datetime.now(timezone.utc).timestamp(),
            "source": "google_oauth",
            "nonce": f"oauth_{datetime.now(timezone.utc).timestamp()}",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10)  # State expires in 10 minutes
        }
        
        state_token = jwt.encode(state_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return state_token
    
    @staticmethod
    def verify_oauth_state(state: str) -> bool:
        """Verify JWT state token"""
        try:
            from jose import jwt, JWTError
            
            payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if it's from our OAuth flow
            if payload.get("source") != "google_oauth":
                return False
                
            return True
            
        except JWTError:
            return False
    
    @staticmethod
    def handle_google_callback(code: str, state: str, db: Session) -> Dict[str, Any]:
        """Handle Google OAuth2 callback and create/login user"""
        try:
            # Verify state token first
            if not GoogleOAuthService.verify_oauth_state(state):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired OAuth state token"
                )
            # Exchange code for token
            flow = GoogleOAuthService.get_google_flow()
            
            # Add error handling for token exchange
            try:
                # Ensure HTTPS is not required for local development
                import os
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
                
                print(f"Attempting to exchange code: {code[:20]}...")
                print(f"Using redirect URI: {settings.GOOGLE_REDIRECT_URI}")
                print(f"Using client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
                
                flow.fetch_token(code=code)
                print("Token exchange successful!")
                
            except Exception as token_error:
                print(f"Token exchange error: {token_error}")
                print(f"Error type: {type(token_error)}")
                print(f"Code received: {code}")
                print(f"Redirect URI: {settings.GOOGLE_REDIRECT_URI}")
                
                # More specific error handling
                error_msg = str(token_error)
                if "Scope has changed" in error_msg:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="OAuth scope configuration error. Please try again."
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to exchange authorization code: {str(token_error)}"
                    )
            
            # Get user info from Google
            credentials = flow.credentials
            user_info_request = requests.Request()
            
            # Add clock skew tolerance for token verification
            try:
                user_info = id_token.verify_oauth2_token(
                    credentials.id_token,
                    user_info_request,
                    settings.GOOGLE_CLIENT_ID,
                    clock_skew_in_seconds=60  # Allow 60 seconds clock skew
                )
            except ValueError as verify_error:
                print(f"Token verification error: {verify_error}")
                # Try alternative method using userinfo endpoint
                userinfo_response = http_requests.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {credentials.token}'}
                )
                if userinfo_response.status_code == 200:
                    user_info = userinfo_response.json()
                    # Add required fields that might be missing
                    user_info['sub'] = user_info.get('id', user_info.get('sub'))
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get user info: {verify_error}"
                    )
            
            # Extract user data
            google_id = user_info.get('sub')
            email = user_info.get('email')
            name = user_info.get('name', '')
            picture = user_info.get('picture', '')
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )
            
            # Check if user exists
            existing_user = UserService.get_user_by_email(db, email)
            
            if existing_user:
                # Update Google ID if not set
                if not existing_user.google_id:
                    existing_user.google_id = google_id
                    db.commit()
                    db.refresh(existing_user)
                
                user = existing_user
            else:
                # Create new user
                username = email.split('@')[0]  # Use email prefix as username
                
                # Ensure username is unique
                counter = 1
                original_username = username
                while UserService.get_user_by_username(db, username):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Create user data
                from schemas.user import UserCreate
                user_data = UserCreate(
                    username=username,
                    email=email,
                    password="google_oauth_user"  # Placeholder password
                )
                
                user = UserService.create_user(db, user_data)
                
                # Update with Google-specific data
                user.google_id = google_id
                user.is_verified = True  # Google users are pre-verified
                if name:
                    user.full_name = name
                if picture:
                    user.avatar_url = picture
                
                db.commit()
                db.refresh(user)
            
            # Create access token
            access_token = AuthService.create_access_token(data={"sub": str(user.id)})
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url
                }
            }
            
        except Exception as e:
            print(f"Google OAuth callback error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authentication failed: {str(e)}"
            )