"""
Supabase authentication backend for Django.

Integrates Supabase Auth with Django's authentication system.

Behaviour:
- In DEVELOPMENT (settings.DEBUG = True):
    * Decodes Supabase JWT locally with signature + audience verification disabled.
    * Extracts email from claims and creates/logs in a Django user.
    * Does NOT call Supabase Auth API (works with local Supabase CLI tokens).

- In PRODUCTION (settings.DEBUG = False):
    * Uses Supabase client auth.get_user(token) to validate the JWT.
    * Creates/updates a Django user from the returned Supabase user object.
"""

import logging
import os

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from supabase import create_client, Client
import jwt

logger = logging.getLogger(__name__)
User = get_user_model()


class SupabaseAuthBackend(BaseBackend):
    """
    Custom authentication backend for Supabase.

    This backend:
    1. Authenticates users using Supabase JWT tokens.
    2. Creates/updates Django User records based on Supabase user data or JWT claims.
    3. Provides helpers for token refresh and sign-out.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ImproperlyConfigured(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables"
            )

        # Supabase client is used for production auth and token operations
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # -------------------------------------------------------------------------
    # Core authentication
    # -------------------------------------------------------------------------
    def authenticate(self, request, token=None, **kwargs):
        """
        Authenticate user using a Supabase JWT access token.

        Args:
            request: Django request object
            token: Supabase JWT access token (string)

        Returns:
            User object if authentication successful, None otherwise.
        """
        if not token:
            return None

        # DEVELOPMENT MODE (local Supabase CLI)
        if getattr(settings, "DEBUG", False):
            return self._authenticate_dev(token)

        # PRODUCTION MODE (hosted Supabase)
        return self._authenticate_prod(token)

    def _authenticate_dev(self, token: str):
        """
        Development-mode authentication.

        - Supabase CLI issues unsigned JWTs.
        - We decode without verifying signature or audience.
        - Email can live in different places in the claims.
        """
        try:
            claims = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                },
            )

            # Try a few locations for email in dev tokens
            email = (
                claims.get("email")
                or (claims.get("user_metadata") or {}).get("email")
                or claims.get("sub")  # fallback if nothing else exists
            )

            if not email:
                logger.error("Supabase dev token missing email-like claim")
                return None

            supabase_id = claims.get("sub")

            # Either find by supabase_id (if your model has it) or by email
            user = None
            if hasattr(User, "supabase_id") and supabase_id:
                try:
                    user = User.objects.get(supabase_id=supabase_id)
                except User.DoesNotExist:
                    user = None

            if user is None:
                # Fallback: get or create by email
                defaults = {"email": email}
                if hasattr(User, "supabase_id") and supabase_id:
                    defaults["supabase_id"] = supabase_id

                user, _ = User.objects.get_or_create(
                    username=email,
                    defaults=defaults,
                )

            return user

        except Exception as e:
            logger.error(f"Supabase dev JWT decode error: {e}")
            return None

    def _authenticate_prod(self, token: str):
        """
        Production-mode authentication.

        Uses Supabase Auth API to verify the JWT and fetch user information.
        """
        try:
            user_data = self.client.auth.get_user(token)
            supabase_user = getattr(user_data, "user", None)

            if not supabase_user:
                logger.warning("Invalid Supabase token provided in production")
                return None

            user = self.get_or_create_user(supabase_user)
            return user

        except Exception as e:
            logger.error(f"Supabase authentication error (prod): {e}")
            return None

    # -------------------------------------------------------------------------
    # Django auth backend required method
    # -------------------------------------------------------------------------
    def get_user(self, user_id):
        """
        Retrieve user by primary key.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # -------------------------------------------------------------------------
    # User mapping helpers
    # -------------------------------------------------------------------------
    def get_or_create_user(self, supabase_user):
        """
        Get or create a Django User from a Supabase user object.

        Args:
            supabase_user: Supabase user object returned from auth.get_user()

        Returns:
            Django User object.
        """
        email = getattr(supabase_user, "email", None)
        supabase_id = getattr(supabase_user, "id", None)
        user_metadata = getattr(supabase_user, "user_metadata", {}) or {}

        if not email:
            logger.error("Supabase user object missing email")
            return None

        try:
            # Prefer matching by supabase_id if your model has it
            if hasattr(User, "supabase_id") and supabase_id:
                user = User.objects.get(supabase_id=supabase_id)
            else:
                user = User.objects.get(email=email)

            # Keep email/username in sync if changed
            updated = False
            if user.email != email:
                user.email = email
                updated = True
            if user.username != email:
                user.username = email
                updated = True

            if updated:
                user.save()

            return user

        except User.DoesNotExist:
            # Create new user
            extra_fields = {
                "email": email,
                "username": email,
            }

            if hasattr(User, "supabase_id") and supabase_id:
                extra_fields["supabase_id"] = supabase_id

            # Optional metadata fields if your model supports them
            first_name = user_metadata.get("first_name", "")
            last_name = user_metadata.get("last_name", "")
            if hasattr(User, "first_name"):
                extra_fields["first_name"] = first_name
            if hasattr(User, "last_name"):
                extra_fields["last_name"] = last_name
            if hasattr(User, "subscription_tier"):
                extra_fields["subscription_tier"] = "free"
            if hasattr(User, "api_credits"):
                extra_fields["api_credits"] = 0

            user = User.objects.create_user(**extra_fields)

            logger.info(f"Created new Django user for Supabase user: {email}")
            return user

    # -------------------------------------------------------------------------
    # Token management helpers (optional)
    # -------------------------------------------------------------------------
    def refresh_token(self, refresh_token: str):
        """
        Refresh Supabase session using a refresh token.

        Returns:
            New session data or None if failed.
        """
        try:
            session = self.client.auth.refresh_session(refresh_token)
            return session
        except Exception as e:
            logger.error(f"Supabase token refresh error: {e}")
            return None

    def sign_out(self, token: str):
        """
        Sign out user from Supabase (invalidate refresh token).

        Args:
            token: Supabase JWT access token (or current session).
        """
        try:
            self.client.auth.sign_out(token)
        except Exception as e:
            logger.error(f"Supabase sign out error: {e}")
