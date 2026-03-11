"""
PayloadOps — Workspace Models

Multi-tenant workspace management with role-based memberships.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from common.mixins import BaseModel


class Workspace(BaseModel):
    """
    Workspace represents a tenant in the multi-tenant system.
    All data (workflows, logs, credentials) is scoped to a workspace.
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    settings = models.JSONField(default=dict, blank=True, help_text="Workspace-specific settings (JSONB)")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "workspaces_workspace"
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class WorkspaceMembership(BaseModel):
    """
    Represents a user's membership in a workspace with a specific role.
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    class Meta:
        db_table = "workspaces_membership"
        verbose_name = "Workspace Membership"
        verbose_name_plural = "Workspace Memberships"
        unique_together = ("user", "workspace")

    def __str__(self) -> str:
        return f"{self.user.email} → {self.workspace.name} ({self.role})"
