import os
import logging
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from supabase import create_client

logger = logging.getLogger(__name__)

# Create Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')  # Use SUPABASE_ANON_KEY from .env

print(f"DEBUG: Supabase URL: {supabase_url}")
print(f"DEBUG: Supabase Key: {supabase_key}")

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
else:
    print("ERROR: Missing Supabase environment variables")
    supabase = None

def login_view(request):
    """
    Display login page with OAuth options
    """
    return render(request, 'auth/login.html')


def logout_view(request):
    """
    Handle user logout
    """
    from django.contrib.auth import logout
    logout(request)
    from django.shortcuts import redirect
    return redirect('login')


def dashboard_view(request):
    """
    Display user dashboard after authentication
    """
    return render(request, 'auth/dashboard.html')


def get_oauth_config(request):
    """
    Return OAuth configuration for frontend
    """
    if not supabase_url:
        return JsonResponse({'error': 'Supabase not configured'}, status=500)
    
    config = {
        'supabaseUrl': supabase_url,
        'supabaseKey': supabase_key,
    }
    return JsonResponse(config)


def refresh_token(request):
    """
    Refresh Supabase authentication token
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return JsonResponse({'error': 'Missing refresh token'}, status=400)
            
            # Use Supabase to refresh the token
            new_session = supabase.auth.refresh_session(refresh_token)
            
            if new_session.session:
                return JsonResponse({
                    'access_token': new_session.session.access_token,
                    'refresh_token': new_session.session.refresh_token,
                })
            else:
                return JsonResponse({'error': 'Failed to refresh token'}, status=400)
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return JsonResponse({'error': 'Token refresh failed'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


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
            from urllib.parse import urlparse, parse_qs
            
            # Get full URL from request
            full_url = request.build_absolute_uri()
            parsed = urlparse(full_url)
            
            print(f"DEBUG: Full URL: {full_url}")
            print(f"DEBUG: Parsed URL: {parsed}")
            print(f"DEBUG: Fragment: {parsed.fragment}")
            
            if parsed.fragment:
                fragment_params = parse_qs(parsed.fragment)
                access_token = fragment_params.get('access_token', [None])[0]
                refresh_token = fragment_params.get('refresh_token', [None])[0]
                print(f"DEBUG: Access token: {access_token[:20] if access_token else 'None'}")
                print(f"DEBUG: Refresh token: {refresh_token[:20] if refresh_token else 'None'}")
        
        if not access_token:
            # For GET requests without access token, return the callback page
            # The JavaScript will handle the token extraction from URL hash
            return render(request, 'auth/callback.html')
        
        # Verify token with Supabase
        user_data = supabase.auth.get_user(access_token)
        
        if not user_data.user:
            logger.warning(f"Invalid Supabase token: {access_token[:10]}...")
            return HttpResponseBadRequest("Invalid token")
        
        # Authenticate with Django backend
        from django.contrib.auth import authenticate
        user = authenticate(request, token=access_token)
        
        if user:
            from django.contrib.auth import login
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
                from django.shortcuts import redirect
                return redirect('dashboard')
        else:
            return HttpResponseBadRequest("Authentication failed")
            
    except Exception as e:
        logger.error(f"Supabase authentication error: {str(e)}")
        return HttpResponseBadRequest("Authentication error")