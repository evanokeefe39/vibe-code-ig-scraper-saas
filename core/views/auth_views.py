"""
Authentication views for Supabase integration
Handles OAuth login, logout, and user session management
"""

import json
import logging
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from supabase import create_client
import os

logger = logging.getLogger(__name__)

# Create Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')  # Use SUPABASE_ANON_KEY from .env
)


def login_view(request):
    """
    Display login page with OAuth options
    """
    return render(request, 'auth/login.html')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def supabase_auth_callback(request):
    """
    Handle Supabase authentication callback
    Supports both GET (OAuth redirect) and POST (AJAX) requests
    """
    try:
        access_token = None
        refresh_token = None
        
        if request.method == 'POST':
            # Handle AJAX POST request
            data = json.loads(request.body)
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
        else:
            # Handle GET request from OAuth redirect
            # Check URL hash for tokens (Supabase puts tokens in hash)
            if request.META.get('HTTP_REFERER') and 'access_token' in request.META['HTTP_REFERER']:
                # Parse from referer if available
                from urllib.parse import urlparse, parse_qs
                referer = request.META['HTTP_REFERER']
                parsed = urlparse(referer)
                if parsed.fragment:
                    from urllib.parse import parse_qs
                    fragment_params = parse_qs(parsed.fragment)
                    access_token = fragment_params.get('access_token', [None])[0]
                    refresh_token = fragment_params.get('refresh_token', [None])[0]
            
            # If no token in referer, check if this is a direct callback with hash
            # This will be handled by JavaScript in the template
        
        if not access_token:
            # For GET requests without tokens, render the callback page that will handle the hash
            if request.method == 'GET':
                return render(request, 'auth/callback.html')
            return HttpResponseBadRequest("Missing access token")
        
        # Verify token with Supabase
        user_data = supabase.auth.get_user(access_token)
        
        if not user_data.user:
            return HttpResponseBadRequest("Invalid token")
        
        # Authenticate with Django backend
        from django.contrib.auth import authenticate
        user = authenticate(request, token=access_token)
        
        if user:
            login(request, user)
            
            # Store tokens in session for future API calls
            request.session['supabase_access_token'] = access_token
            request.session['supabase_refresh_token'] = refresh_token
            
            if request.method == 'POST':
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/auth/dashboard/'
                })
            else:
                # For GET requests, redirect to dashboard
                return redirect('dashboard')
        else:
            return HttpResponseBadRequest("Authentication failed")
            
    except Exception as e:
        logger.error(f"Auth callback error: {str(e)}")
        return HttpResponseBadRequest("Authentication error")


@login_required
def logout_view(request):
    """
    Log out user from both Django and Supabase
    """
    try:
        # Sign out from Supabase if we have a token
        access_token = request.session.get('supabase_access_token')
        if access_token:
            supabase.auth.sign_out(access_token)
        
        # Log out from Django
        logout(request)
        
        return redirect('login')
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Still logout from Django even if Supabase fails
        logout(request)
        return redirect('login')


@login_required
def dashboard_view(request):
    """
    User dashboard after successful login
    """
    from core.models import Run, UserList
    
    # Get user statistics
    run_count = Run.objects.filter(user_id=request.user.id).count()
    list_count = UserList.objects.filter(user=request.user).count()
    recent_runs = Run.objects.filter(user_id=request.user.id).order_by('-created_at')[:5]
    
    context = {
        'run_count': run_count,
        'list_count': list_count,
        'recent_runs': recent_runs,
        'api_credits': 100  # TODO: Implement API credit system
    }
    
    return render(request, 'auth/dashboard.html', context)


def get_oauth_config(request):
    """
    Return OAuth configuration for frontend
    """
    config = {
        'supabaseUrl': os.getenv('SUPABASE_URL'),
        'supabaseAnonKey': os.getenv('SUPABASE_ANON_KEY'),  # Use SUPABASE_ANON_KEY from .env
        'providers': {
            'google': {
                'name': 'Google',
                'icon': 'google-color',
                'enabled': True
            },
            'apple': {
                'name': 'Apple',
                'icon': 'apple-black',
                'enabled': True
            }
        }
    }
    
    return JsonResponse(config)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    Refresh Supabase JWT token
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return HttpResponseBadRequest("Missing refresh token")
        
        # Refresh token with Supabase
        session = supabase.auth.refresh_session(refresh_token)
        
        if session.session:
            # Update session tokens
            request.session['supabase_access_token'] = session.session.access_token
            request.session['supabase_refresh_token'] = session.session.refresh_token
            
            return JsonResponse({
                'success': True,
                'access_token': session.session.access_token
            })
        else:
            return HttpResponseBadRequest("Token refresh failed")
            
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return HttpResponseBadRequest("Token refresh error")