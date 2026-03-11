"""
PayloadOps — Execution Log Model

Detailed logging for each workflow execution, including the payload
received, response from the destination, status, and retry information.
"""

from __future__ import annotations

from django.db import models

from common.mixins import TenantModel


class ExecutionLog(TenantModel):
    """
    Records every webhook execution attempt with full audit trail.
    Stores both the inbound payload and outbound response for debugging.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"
        DEAD_LETTER = "dead_letter", "Dead Letter"

    workflow = models.ForeignKey(
        "workflows.Workflow",
        on_delete=models.CASCADE,
        related_name="execution_logs",
    )
    trigger = models.ForeignKey(
        "workflows.Trigger",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="execution_logs",
    )
    action = models.ForeignKey(
        "workflows.Action",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="execution_logs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Inbound data
    payload_received = models.JSONField(
        default=dict,
        help_text="The JSON payload received from the webhook",
    )

    # Outbound data
    response_body = models.JSONField(
        default=None,
        null=True,
        blank=True,
        help_text="Response body from the destination service",
    )
    response_status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP status code from the destination",
    )

    # Execution metadata
    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Current attempt number (1 = first try)",
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Maximum retry attempts configured",
    )
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Execution duration in milliseconds",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error details if execution failed",
    )

    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantModel.Meta):
        db_table = "observability_execution_log"
        verbose_name = "Execution Log"
        verbose_name_plural = "Execution Logs"
        indexes = [
            models.Index(fields=["workflow", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Execution {self.id} [{self.status}] — {self.workflow.name}"
