"""
PayloadOps — Workflow Models

Defines the core domain models: Workflow, Trigger, Action, and Credential.
These models orchestrate the webhook ingestion and outbound action pipeline.
"""

from __future__ import annotations

import uuid

from django.db import models

from common.encryption import decrypt_value, encrypt_value
from common.mixins import TenantModel


class Workflow(TenantModel):
    """
    A workflow connects a Trigger (webhook) to one or more Actions (outbound HTTP).
    Represents the full integration pipeline configured by the user.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    class Meta(TenantModel.Meta):
        db_table = "workflows_workflow"
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"

    def __str__(self) -> str:
        return f"{self.name} [{self.status}]"

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE


class Trigger(TenantModel):
    """
    A Trigger generates a unique webhook URL for receiving inbound data.
    Each trigger is linked to exactly one workflow.
    """

    class TriggerType(models.TextChoices):
        WEBHOOK = "webhook", "Webhook"

    workflow = models.OneToOneField(
        Workflow,
        on_delete=models.CASCADE,
        related_name="trigger",
    )
    trigger_type = models.CharField(
        max_length=20,
        choices=TriggerType.choices,
        default=TriggerType.WEBHOOK,
    )
    webhook_path = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        help_text="Unique UUID path for the webhook URL",
    )
    is_active = models.BooleanField(default=True)

    class Meta(TenantModel.Meta):
        db_table = "workflows_trigger"
        verbose_name = "Trigger"
        verbose_name_plural = "Triggers"

    def __str__(self) -> str:
        return f"Trigger: {self.webhook_path} → {self.workflow.name}"

    @property
    def webhook_url(self) -> str:
        """Generate the full webhook URL path."""
        return f"/hooks/{self.webhook_path}/"


class Action(TenantModel):
    """
    An Action defines an outbound HTTP request to a destination service.
    Actions are executed in order after a webhook payload is received.
    """

    class HttpMethod(models.TextChoices):
        GET = "GET", "GET"
        POST = "POST", "POST"
        PUT = "PUT", "PUT"
        PATCH = "PATCH", "PATCH"
        DELETE = "DELETE", "DELETE"

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Execution order within the workflow",
    )
    http_method = models.CharField(
        max_length=10,
        choices=HttpMethod.choices,
        default=HttpMethod.POST,
    )
    url = models.URLField(
        max_length=2000,
        help_text="Destination URL for the outbound request",
    )
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="HTTP headers (JSONB) — may include template variables",
    )
    body_template = models.JSONField(
        default=dict,
        blank=True,
        help_text="Body template with variable injection (e.g., {{payload.field}})",
    )
    is_active = models.BooleanField(default=True)

    class Meta(TenantModel.Meta):
        db_table = "workflows_action"
        verbose_name = "Action"
        verbose_name_plural = "Actions"
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.name} [{self.http_method} → {self.url}]"


class Credential(TenantModel):
    """
    Encrypted credential storage for external API tokens.
    Values are encrypted at rest using Fernet symmetric encryption.
    """

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    encrypted_value = models.TextField(help_text="Fernet-encrypted credential value")

    class Meta(TenantModel.Meta):
        db_table = "workflows_credential"
        verbose_name = "Credential"
        verbose_name_plural = "Credentials"

    def __str__(self) -> str:
        return self.name

    def set_value(self, plaintext: str) -> None:
        """Encrypt and store a credential value."""
        self.encrypted_value = encrypt_value(plaintext)

    def get_value(self) -> str:
        """Decrypt and return the credential value."""
        return decrypt_value(self.encrypted_value)
