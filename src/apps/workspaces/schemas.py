"""
PayloadOps — Workspace API Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime

from ninja import Schema
from pydantic import Field


class WorkspaceCreateInput(Schema):
    """Input schema for creating a workspace."""

    name: str = Field(min_length=2, max_length=100)
    description: str = ""


class WorkspaceUpdateInput(Schema):
    """Input schema for updating a workspace."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None


class WorkspaceOutput(Schema):
    """Output schema for workspace."""

    id: uuid.UUID
    name: str
    slug: str
    description: str
    is_active: bool
    created_at: datetime


class MembershipOutput(Schema):
    """Output schema for workspace membership."""

    id: uuid.UUID
    user_email: str
    role: str
    created_at: datetime

    @staticmethod
    def resolve_user_email(obj) -> str:
        return obj.user.email


class InviteMemberInput(Schema):
    """Input schema for inviting a member to a workspace."""

    email: str
    role: str = "member"
