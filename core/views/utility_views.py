from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('dashboard')
    return render(request, 'home.html')


def pricing(request):
    return render(request, 'pricing.html')