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
from django.conf import settings
from django.conf.urls.static import static
from core.utility_views import home, test_geocode
from core.views.run_views import run_create, run_list, run_detail, run_by_n8n, run_status_api, empty_source_form, platform_config
from core.views.list_views import list_list, list_detail, list_create, list_column_create, list_row_create, update_cell, delete_row, add_blank_row, update_column, delete_column, delete_list, table_save, validate_column_type_change
from core.views.export_views import export_list_csv, export_list_json, export_run_csv, export_run_json

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("test-geocode/", test_geocode, name="test_geocode"),
    path("runs/", run_list, name="run_list"),
path("runs/create/", run_create, name="run_create"),
    path("runs/create/empty-form/", empty_source_form, name="empty_source_form"),
    path("runs/create/platform-config/<str:platform_type>/", platform_config, name="platform_config"),
    path("runs/<int:pk>/", run_detail, name="run_detail"),
    path("runs/<int:pk>/status/", run_status_api, name="run_status_api"),
    path("runs/<int:pk>/export/csv/", export_run_csv, name="export_run_csv"),
    path("runs/<int:pk>/export/json/", export_run_json, name="export_run_json"),
    path("runs/by-n8n/<int:n8n_execution_id>/", run_by_n8n, name="run_by_n8n"),
    # User List Management
    path("lists/", list_list, name="list_list"),
    path("lists/create/", list_create, name="list_create"),
    path("lists/<int:pk>/", list_detail, name="list_detail"),
    path("lists/<int:pk>/columns/create/", list_column_create, name="list_column_create"),
    path("lists/<int:pk>/columns/<int:column_id>/update/", update_column, name="update_column"),
    path("lists/<int:pk>/columns/<int:column_id>/validate/", validate_column_type_change, name="validate_column_type_change"),
    path("lists/<int:pk>/columns/<int:column_id>/delete/", delete_column, name="delete_column"),
    path("lists/<int:pk>/delete/", delete_list, name="delete_list"),
    path("lists/<int:pk>/rows/create/", list_row_create, name="list_row_create"),
    path("lists/<int:pk>/rows/update/", update_cell, name="update_cell"),
    path("lists/<int:pk>/rows/delete/", delete_row, name="delete_row"),
    path("lists/<int:pk>/rows/add-blank/", add_blank_row, name="add_blank_row"),
    path("lists/<int:pk>/table/save/", table_save, name="table_save"),
    path("lists/<int:pk>/export/csv/", export_list_csv, name="export_list_csv"),
    path("lists/<int:pk>/export/json/", export_list_json, name="export_list_json"),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
