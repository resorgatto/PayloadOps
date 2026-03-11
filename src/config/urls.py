"""
SEAM — URL Configuration
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from config.api import api


def health_check(request):
    """Simple health check endpoint for Docker/load balancer."""
    return JsonResponse({"status": "healthy", "service": "seam"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/health/", health_check, name="health-check"),
]
