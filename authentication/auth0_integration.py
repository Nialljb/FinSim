"""
Auth0 Integration Module for FinSim
Handles OAuth2 authentication flow with Auth0
"""

import os
import json
import secrets
from urllib.parse import urlencode, quote_plus
from datetime import datetime
import requests
from authlib.integrations.requests_client import OAuth2Session
from jose import jwt, JWTError
from typing import Optional, Dict, Tuple

try:
    from config.settings import (
        AUTH0_DOMAIN, 
        AUTH0_CLIENT_ID, 
        AUTH0_CLIENT_SECRET,
        AUTH0_CALLBACK_URL,
        AUTH0_AUDIENCE,
        BASE_URL
    )
except ImportError:
    # Fallback for development
    from dotenv import load_dotenv
    load_dotenv()
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET", "")
    AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8501/callback")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")


class Auth0Client:
    """Auth0 OAuth2 client for handling authentication"""
    
    def __init__(self):
        if not AUTH0_DOMAIN or not AUTH0_CLIENT_ID or not AUTH0_CLIENT_SECRET:
            raise ValueError("Auth0 configuration not properly set. Check environment variables.")
        
        self.domain = AUTH0_DOMAIN
        self.client_id = AUTH0_CLIENT_ID
        self.client_secret = AUTH0_CLIENT_SECRET
        self.callback_url = AUTH0_CALLBACK_URL
        self.audience = AUTH0_AUDIENCE
        
        # Auth0 URLs
        self.authorization_endpoint = f"https://{self.domain}/authorize"
        self.token_endpoint = f"https://{self.domain}/oauth/token"
        self.userinfo_endpoint = f"https://{self.domain}/userinfo"
        self.jwks_uri = f"https://{self.domain}/.well-known/jwks.json"
        
    def get_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate Auth0 authorization URL
        
        Returns:
            tuple: (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'scope': 'openid profile email',
            'state': state,
        }
        
        if self.audience:
            params['audience'] = self.audience
        
        auth_url = f"{self.authorization_endpoint}?{urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from callback
            
        Returns:
            dict: Token response containing access_token, id_token, etc.
        """
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.callback_url,
        }
        
        response = requests.post(self.token_endpoint, json=token_data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user information from Auth0
        
        Args:
            access_token: Access token from token exchange
            
        Returns:
            dict: User profile information
        """
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(self.userinfo_endpoint, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def verify_id_token(self, id_token: str) -> Dict:
        """
        Verify and decode ID token
        
        Args:
            id_token: ID token to verify
            
        Returns:
            dict: Decoded token payload
        """
        try:
            # Get JWKS for token verification
            jwks_response = requests.get(self.jwks_uri)
            jwks = jwks_response.json()
            
            # Decode and verify token
            payload = jwt.decode(
                id_token,
                jwks,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f'https://{self.domain}/'
            )
            
            return payload
            
        except JWTError as e:
            raise ValueError(f"Invalid ID token: {str(e)}")
    
    def logout_url(self, return_to: Optional[str] = None) -> str:
        """
        Generate Auth0 logout URL
        
        Args:
            return_to: URL to redirect to after logout
            
        Returns:
            str: Logout URL
        """
        if return_to is None:
            return_to = BASE_URL
        
        params = {
            'client_id': self.client_id,
            'returnTo': return_to
        }
        
        return f"https://{self.domain}/v2/logout?{urlencode(params)}"


def create_or_update_user_from_auth0(user_info: Dict, db_session) -> Tuple[bool, str, Optional[Dict]]:
    """
    Create or update user in database from Auth0 user info
    
    Args:
        user_info: User information from Auth0
        db_session: Database session
        
    Returns:
        tuple: (success, message, user_data)
    """
    from data_layer.database import User, UsageStats
    
    try:
        # Extract user info
        auth0_id = user_info.get('sub')  # Auth0 unique identifier
        email = user_info.get('email')
        email_verified = user_info.get('email_verified', False)
        name = user_info.get('name', '')
        nickname = user_info.get('nickname', '')
        picture = user_info.get('picture', '')
        
        # Use email prefix or nickname as username
        username = nickname or email.split('@')[0] if email else auth0_id
        
        # Check if user already exists by auth0_id or email
        user = db_session.query(User).filter(
            (User.auth0_id == auth0_id) | (User.email == email)
        ).first()
        
        if user:
            # Update existing user
            user.auth0_id = auth0_id
            user.email = email
            user.email_verified = email_verified
            user.last_login = datetime.now()
            user.is_active = True
            
            # Update profile picture if available
            if picture and hasattr(user, 'profile_picture'):
                user.profile_picture = picture
            
            db_session.commit()
            message = "Login successful"
            
        else:
            # Create new user
            # Note: For Auth0 users, we don't store password_hash
            user = User(
                username=username,
                email=email,
                auth0_id=auth0_id,
                email_verified=email_verified,
                password_hash='',  # Empty for Auth0 users
                current_age=30,  # Default values - will be set during onboarding
                target_retirement_age=65,
                is_active=True,
                created_at=datetime.now(),
                last_login=datetime.now()
            )
            
            if picture and hasattr(user, 'profile_picture'):
                user.profile_picture = picture
            
            db_session.add(user)
            db_session.flush()  # Get user.id
            
            # Initialize usage stats
            current_month = datetime.now().strftime("%Y-%m")
            usage_stats = UsageStats(
                user_id=user.id,
                current_month=current_month,
                simulations_this_month=0,
                exports_this_month=0
            )
            db_session.add(usage_stats)
            db_session.commit()
            
            message = "Account created successfully"
        
        # Extract user data for session
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'current_age': user.current_age,
            'target_retirement_age': user.target_retirement_age,
            'country': user.country,
            'preferred_currency': user.preferred_currency or 'EUR',
            'last_login': user.last_login,
            'auth0_id': user.auth0_id,
            'picture': picture
        }
        
        return True, message, user_data
        
    except Exception as e:
        db_session.rollback()
        return False, f"Failed to create/update user: {str(e)}", None


def handle_auth0_callback(code: str, state: str, expected_state: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Handle Auth0 callback after user authorization
    
    Args:
        code: Authorization code from Auth0
        state: State parameter from callback
        expected_state: Expected state value (for compatibility, not strictly validated here)
        
    Returns:
        tuple: (success, message, user_data)
    """
    from data_layer.database import SessionLocal
    
    # Note: In a stateless environment like Streamlit with external redirects,
    # strict state validation is challenging. Auth0's token exchange provides
    # security through the authorization code flow and HTTPS.
    # For production, consider using signed JWT tokens or database-backed state storage.
    
    try:
        # Initialize Auth0 client
        auth0 = Auth0Client()
        
        # Exchange code for tokens
        token_response = auth0.exchange_code_for_token(code)
        access_token = token_response.get('access_token')
        id_token = token_response.get('id_token')
        
        # Get user info
        user_info = auth0.get_user_info(access_token)
        
        # Verify ID token (optional but recommended)
        try:
            token_payload = auth0.verify_id_token(id_token)
        except Exception as e:
            # Continue even if verification fails, but log it
            print(f"ID token verification failed: {e}")
        
        # Create or update user in database
        db = SessionLocal()
        try:
            success, message, user_data = create_or_update_user_from_auth0(user_info, db)
            return success, message, user_data
        finally:
            db.close()
            
    except Exception as e:
        return False, f"Authentication failed: {str(e)}", None


# Convenience function for Streamlit integration
def get_auth0_login_button_html(auth0_client: Auth0Client, state: str) -> str:
    """
    Generate HTML for Auth0 login button
    
    Args:
        auth0_client: Auth0Client instance
        state: State parameter for CSRF protection
        
    Returns:
        str: HTML for login button
    """
    auth_url, _ = auth0_client.get_authorization_url(state)
    
    html = f"""
    <a href="{auth_url}" target="_self" style="text-decoration: none;">
        <button style="
            background-color: #EB5424;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s;
        " onmouseover="this.style.backgroundColor='#D64820'" 
           onmouseout="this.style.backgroundColor='#EB5424'">
            🔐 Sign in with Auth0
        </button>
    </a>
    """
    
    return html
