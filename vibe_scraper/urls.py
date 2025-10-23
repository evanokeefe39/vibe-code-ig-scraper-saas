"""
URL configuration for vibe_scraper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core.views import home, test_geocode, run_create, run_list, run_detail, run_by_n8n

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("test-geocode/", test_geocode, name="test_geocode"),
    path("runs/", run_list, name="run_list"),
    path("runs/create/", run_create, name="run_create"),
    path("runs/<int:pk>/", run_detail, name="run_detail"),
    path("runs/by-n8n/<int:n8n_execution_id>/", run_by_n8n, name="run_by_n8n"),
]
