"""
PayloadOps — Workspace API Endpoints

CRUD operations for workspaces and membership management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ninja import Router

from apps.accounts.auth import auth
from apps.accounts.schemas import MessageOutput
from apps.workspaces.models import Workspace, WorkspaceMembership
from apps.workspaces.schemas import (
    InviteMemberInput,
    MembershipOutput,
    WorkspaceCreateInput,
    WorkspaceOutput,
    WorkspaceUpdateInput,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

router = Router()


# ==========================================
# Workspace CRUD
# ==========================================


@router.post("/", auth=auth, response={201: WorkspaceOutput})
def create_workspace(request: HttpRequest, payload: WorkspaceCreateInput):
    """Create a new workspace. The creator becomes the owner."""
    workspace = Workspace.objects.create(
        name=payload.name,
        description=payload.description,
    )

    # Create owner membership
    WorkspaceMembership.objects.create(
        user=request.auth,
        workspace=workspace,
        role=WorkspaceMembership.Role.OWNER,
    )

    return 201, workspace


@router.get("/", auth=auth, response=list[WorkspaceOutput])
def list_workspaces(request: HttpRequest):
    """List all workspaces the current user belongs to."""
    return Workspace.objects.filter(
        memberships__user=request.auth,
        is_active=True,
    )


@router.get("/{workspace_id}", auth=auth, response={200: WorkspaceOutput, 404: MessageOutput})
def get_workspace(request: HttpRequest, workspace_id: str):
    """Get details of a specific workspace."""
    workspace = Workspace.objects.filter(
        id=workspace_id,
        memberships__user=request.auth,
    ).first()

    if workspace is None:
        return 404, {"detail": "Workspace not found."}

    return 200, workspace


@router.patch("/{workspace_id}", auth=auth, response={200: WorkspaceOutput, 404: MessageOutput})
def update_workspace(request: HttpRequest, workspace_id: str, payload: WorkspaceUpdateInput):
    """Update a workspace (admin/owner only)."""
    membership = WorkspaceMembership.objects.filter(
        workspace_id=workspace_id,
        user=request.auth,
        role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
    ).first()

    if membership is None:
        return 404, {"detail": "Workspace not found or insufficient permissions."}

    workspace = membership.workspace
    if payload.name is not None:
        workspace.name = payload.name
    if payload.description is not None:
        workspace.description = payload.description
    workspace.save()

    return 200, workspace


# ==========================================
# Membership Management
# ==========================================


@router.get("/{workspace_id}/members", auth=auth, response=list[MembershipOutput])
def list_members(request: HttpRequest, workspace_id: str):
    """List all members of a workspace."""
    return WorkspaceMembership.objects.filter(
        workspace_id=workspace_id,
        workspace__memberships__user=request.auth,
    ).select_related("user")


@router.post(
    "/{workspace_id}/members",
    auth=auth,
    response={201: MembershipOutput, 400: MessageOutput, 404: MessageOutput},
)
def invite_member(request: HttpRequest, workspace_id: str, payload: InviteMemberInput):
    """Invite a user to a workspace (admin/owner only)."""
    from apps.accounts.models import User

    # Check the requester is admin/owner
    membership = WorkspaceMembership.objects.filter(
        workspace_id=workspace_id,
        user=request.auth,
        role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
    ).first()

    if membership is None:
        return 404, {"detail": "Workspace not found or insufficient permissions."}

    # Find the user to invite
    invited_user = User.objects.filter(email=payload.email).first()
    if invited_user is None:
        return 400, {"detail": "User with this email not found."}

    # Check if already a member
    if WorkspaceMembership.objects.filter(workspace_id=workspace_id, user=invited_user).exists():
        return 400, {"detail": "User is already a member of this workspace."}

    new_membership = WorkspaceMembership.objects.create(
        user=invited_user,
        workspace_id=workspace_id,
        role=payload.role,
    )

    return 201, new_membership


@router.delete(
    "/{workspace_id}/members/{member_id}",
    auth=auth,
    response={200: MessageOutput, 404: MessageOutput},
)
def remove_member(request: HttpRequest, workspace_id: str, member_id: str):
    """Remove a member from a workspace (admin/owner only)."""
    # Check requester permissions
    requester_membership = WorkspaceMembership.objects.filter(
        workspace_id=workspace_id,
        user=request.auth,
        role__in=[WorkspaceMembership.Role.OWNER, WorkspaceMembership.Role.ADMIN],
    ).first()

    if requester_membership is None:
        return 404, {"detail": "Workspace not found or insufficient permissions."}

    target_membership = WorkspaceMembership.objects.filter(
        id=member_id,
        workspace_id=workspace_id,
    ).first()

    if target_membership is None:
        return 404, {"detail": "Membership not found."}

    if target_membership.role == WorkspaceMembership.Role.OWNER:
        return 400, {"detail": "Cannot remove the workspace owner."}

    target_membership.delete()
    return 200, {"detail": "Member removed successfully."}
