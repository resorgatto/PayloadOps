"""
PayloadOps — Workflow Admin Configuration
"""

from django.contrib import admin

from apps.workflows.models import Action, Credential, Trigger, Workflow


class TriggerInline(admin.StackedInline):
    model = Trigger
    extra = 0
    readonly_fields = ("webhook_path", "created_at")


class ActionInline(admin.TabularInline):
    model = Action
    extra = 0
    ordering = ("order",)


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "status", "created_at", "updated_at")
    list_filter = ("status", "workspace")
    search_fields = ("name", "description")
    inlines = [TriggerInline, ActionInline]


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ("webhook_path", "workflow", "trigger_type", "is_active", "created_at")
    list_filter = ("trigger_type", "is_active")
    readonly_fields = ("webhook_path",)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("name", "workflow", "http_method", "url", "order", "is_active")
    list_filter = ("http_method", "is_active")
    search_fields = ("name", "url")


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "created_at")
    search_fields = ("name",)
    readonly_fields = ("encrypted_value",)
