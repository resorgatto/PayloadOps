"""
SEAM — Accounts Admin Configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import APIKey, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "full_name", "is_verified", "is_staff", "created_at")
    list_filter = ("is_verified", "is_staff", "is_active")
    search_fields = ("email", "username", "full_name")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (("Profile", {"fields": ("full_name", "is_verified")}),)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "user", "workspace", "is_active", "last_used_at", "created_at")
    list_filter = ("is_active", "workspace")
    search_fields = ("name", "prefix", "user__email")
    readonly_fields = ("hashed_key", "prefix", "created_at", "updated_at")
