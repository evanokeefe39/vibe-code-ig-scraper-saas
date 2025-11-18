import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.conf import settings
from django.http import JsonResponse
import requests
import json

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Redirect to Supabase authentication
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # For development, create a simple login form or redirect to Supabase
    supabase_url = getattr(settings, 'SUPABASE_URL')
    return render(request, 'auth/login.html', {
        'supabase_url': supabase_url
    })

def callback_page(request):
    return render(request, "auth/callback.html")

def logout_view(request):
    """
    Logout user and redirect to home
    """
    logout(request)
    return redirect('home')

def dashboard_view(request):
    """
    Display user dashboard after authentication
    """
    if request.user.is_authenticated:
        try:
            from core.models import UserList, Run
            
            # Get actual counts for UserList (uses proper ForeignKey)
            list_count = UserList.objects.filter(user=request.user).count()
            
# Get runs for current user - Run model now uses proper ForeignKey
            run_count = Run.objects.filter(user=request.user).count()
            
            # Get recent runs for current user
            recent_runs = Run.objects.filter(user=request.user).order_by('-created_at')[:5]
            
            context = {
                'list_count': list_count,
                'run_count': run_count,
                'recent_runs': recent_runs,
                'api_credits': getattr(request.user, 'api_credits', 100)
            }
            
            return render(request, 'auth/dashboard.html', context)
        except Exception as e:
            logger.error(f"Error in dashboard view: {e}")
            # Return empty context on error
            return render(request, 'auth/dashboard.html', {
                'list_count': 0,
                'run_count': 0,
                'recent_runs': [],
                'api_credits': 100
            })
    else:
        return redirect('login')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def supabase_auth_callback(request):
    """
    Handle Supabase authentication callback
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            
            if not access_token:
                return JsonResponse({'success': False, 'error': 'No access token provided'})
            
            # Use custom authentication backend to verify token and create/update user
            from core.auth_backends import SupabaseAuthBackend
            backend = SupabaseAuthBackend()
            user = backend.authenticate(request, token=access_token)
            
            if user:
                # Log in user
                login(request, user, backend='core.auth_backends.SupabaseAuthBackend')
                
                # Store refresh token in session for later use
                if refresh_token:
                    request.session['supabase_refresh_token'] = refresh_token
                
                return JsonResponse({'success': True, 'redirect_url': '/auth/dashboard/'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid token'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            logger.error(f"Supabase auth callback error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Authentication failed'})
    
    # Handle GET request (OAuth redirect with hash)
    elif request.method == 'GET':
        # This handles the redirect from OAuth provider with tokens in URL hash
        return render(request, 'auth/callback.html')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def refresh_token(request):
    """
    Refresh authentication token
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                # Try to get from session
                refresh_token = request.session.get('supabase_refresh_token')
            
            if not refresh_token:
                return JsonResponse({'success': False, 'error': 'No refresh token provided'})
            
            # Use auth backend to refresh token
            from core.auth_backends import SupabaseAuthBackend
            backend = SupabaseAuthBackend()
            session = backend.refresh_token(refresh_token)
            
            if session and session.access_token:
                # Get user with new token
                user = backend.authenticate(request, token=session.access_token)
                if user:
                    login(request, user, backend='core.auth_backends.SupabaseAuthBackend')
                    
                    # Update session with new refresh token
                    if session.refresh_token:
                        request.session['supabase_refresh_token'] = session.refresh_token
                    
                    return JsonResponse({
                        'success': True, 
                        'access_token': session.access_token,
                        'refresh_token': session.refresh_token
                    })
            
            return JsonResponse({'success': False, 'error': 'Failed to refresh token'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Token refresh failed'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_oauth_config(request):
    """
    Return OAuth configuration for frontend
    """
    config = {
        'supabaseUrl': getattr(settings, 'SUPABASE_URL', ''),
        'supabaseKey': getattr(settings, 'SUPABASE_ANON_KEY', ''),
    }
    return JsonResponse(config)
