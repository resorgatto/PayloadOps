"""
PayloadOps — Observability Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.observability.models import ExecutionLog


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "workflow",
        "status_badge",
        "attempt_number",
        "response_status_code",
        "duration_ms",
        "created_at",
    )
    list_filter = ("status", "workspace", "workflow")
    search_fields = ("id", "workflow__name", "error_message")
    readonly_fields = (
        "payload_received",
        "response_body",
        "started_at",
        "completed_at",
        "created_at",
    )
    date_hierarchy = "created_at"

    def short_id(self, obj) -> str:
        return str(obj.id)[:8]

    short_id.short_description = "ID"  # type: ignore[attr-defined]

    def status_badge(self, obj) -> str:
        colors = {
            "success": "#28a745",
            "failed": "#dc3545",
            "pending": "#ffc107",
            "processing": "#17a2b8",
            "retrying": "#fd7e14",
            "dead_letter": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"  # type: ignore[attr-defined]
