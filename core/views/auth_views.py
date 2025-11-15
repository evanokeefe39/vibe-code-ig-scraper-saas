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
    supabase_url = getattr(settings, 'SUPABASE_URL', 'https://your-project.supabase.co')
    return render(request, 'auth/login.html', {
        'supabase_url': supabase_url
    })

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

def supabase_auth_callback(request):
    """
    Handle Supabase authentication callback
    """
    # This would handle the OAuth callback from Supabase
    # For now, just redirect to dashboard
    return redirect('dashboard')

def get_oauth_config(request):
    """
    Return OAuth configuration for frontend
    """
    config = {
        'supabaseUrl': getattr(settings, 'SUPABASE_URL', ''),
        'supabaseKey': getattr(settings, 'SUPABASE_ANON_KEY', ''),
    }
    return JsonResponse(config)

def refresh_token(request):
    """
    Refresh authentication token
    """
    # This would handle token refresh logic
    return JsonResponse({'status': 'success'})