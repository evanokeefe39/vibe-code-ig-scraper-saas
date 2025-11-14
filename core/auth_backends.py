"""
Supabase authentication backend for Django
Integrates Supabase auth with Django's user authentication system
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from supabase import create_client, Client
import os
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class SupabaseAuthBackend(BaseBackend):
    """
    Custom authentication backend for Supabase
    
    This backend:
    1. Authenticates users using Supabase JWT tokens
    2. Creates/updates Django User records based on Supabase user data
    3. Manages user sessions and authentication state
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')  # Use SUPABASE_ANON_KEY from .env
        
        if not self.supabase_url or not self.supabase_key:
            raise ImproperlyConfigured(
                "SUPABASE_URL and SUPABASE_API_KEY must be set in environment variables"
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def authenticate(self, request, token=None, **kwargs):
        """
        Authenticate user using Supabase JWT token
        
        Args:
            request: Django request object
            token: Supabase JWT token
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if not token:
            return None
            
        try:
            # Verify JWT token with Supabase
            user_data = self.client.auth.get_user(token)
            
            if not user_data.user:
                logger.warning("Invalid Supabase token provided")
                return None
                
            # Get or create Django user
            user = self.get_or_create_user(user_data.user)
            return user
            
        except Exception as e:
            logger.error(f"Supabase authentication error: {str(e)}")
            return None
    
    def get_user(self, user_id):
        """
        Retrieve user by primary key
        
        Args:
            user_id: Django user primary key
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def get_or_create_user(self, supabase_user):
        """
        Get or create Django user from Supabase user data
        
        Args:
            supabase_user: Supabase user object
            
        Returns:
            Django User object
        """
        try:
            # Try to find existing user by supabase_id
            user = User.objects.get(supabase_id=supabase_user.id)
            
            # Update user data if needed
            if user.email != supabase_user.email:
                user.email = supabase_user.email
                user.username = supabase_user.email  # Keep username in sync
                user.save()
                
            return user
            
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=supabase_user.email,
                email=supabase_user.email,
                first_name=supabase_user.user_metadata.get('first_name', ''),
                last_name=supabase_user.user_metadata.get('last_name', ''),
                supabase_id=supabase_user.id,
                subscription_tier='free'  # Default subscription tier
            )
            
            logger.info(f"Created new Django user for Supabase user: {supabase_user.email}")
            return user
    
    def refresh_token(self, refresh_token):
        """
        Refresh Supabase JWT token
        
        Args:
            refresh_token: Supabase refresh token
            
        Returns:
            New session data or None if failed
        """
        try:
            session = self.client.auth.refresh_session(refresh_token)
            return session
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return None
    
    def sign_out(self, token):
        """
        Sign out user from Supabase
        
        Args:
            token: Supabase JWT token
        """
        try:
            self.client.auth.sign_out(token)
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")