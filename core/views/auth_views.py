def dashboard_view(request):
    """
    Display user dashboard after authentication
    """
    if request.user.is_authenticated:
        try:
            from core.models import UserList, Run
            
            # Get actual counts
            list_count = UserList.objects.filter(user=request.user).count()
            run_count = Run.objects.filter(user=request.user).count()
            
            context = {
                'list_count': list_count,
                'run_count': run_count,
                'api_credits': getattr(request.user, 'api_credits', 100)
            }
            
            return render(request, 'auth/dashboard.html', context)
        except Exception as e:
            logger.error(f"Error in dashboard view: {e}")
            return render(request, 'auth/dashboard.html')
    else:
        return render(request, 'auth/dashboard.html')