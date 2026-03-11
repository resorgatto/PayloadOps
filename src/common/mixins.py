"""
PayloadOps — Tenant Isolation Mixins

Provides querysets and model mixins that automatically filter
data by the active workspace, ensuring strict multi-tenant isolation.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    pass


class TenantQuerySet(models.QuerySet):
    """QuerySet that can be filtered by workspace."""

    def for_workspace(self, workspace) -> TenantQuerySet:
        """Filter queryset to only include records for the given workspace."""
        return self.filter(workspace=workspace)


class TenantManager(models.Manager):
    """Manager that returns TenantQuerySet."""

    def get_queryset(self) -> TenantQuerySet:
        return TenantQuerySet(self.model, using=self._db)

    def for_workspace(self, workspace) -> TenantQuerySet:
        return self.get_queryset().for_workspace(workspace)


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamps.
    All models in PayloadOps should inherit from this.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantModel(BaseModel):
    """
    Abstract model for workspace-scoped entities.
    Provides automatic tenant isolation via TenantManager.
    """

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True,
    )

    objects = TenantManager()

    class Meta(BaseModel.Meta):
        abstract = True
