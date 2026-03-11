"""
SEAM — Workspace Middleware

Injects the active workspace into every request based on the
X-Workspace-ID header or API key context, ensuring strict tenant isolation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.http import JsonResponse

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

# Paths that don't require workspace context
EXEMPT_PATHS = (
    "/admin/",
    "/api/health/",
    "/api/auth/register",
    "/api/auth/login",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/hooks/",
)


class WorkspaceMiddleware:
    """
    Middleware that resolves the workspace from the request.

    For authenticated API requests, reads the X-Workspace-ID header
    and validates that the user has access to that workspace.
    Webhook ingestion endpoints are exempt (resolved by webhook path).
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.workspace = None  # type: ignore[attr-defined]

        # Skip workspace resolution for exempt paths
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            return self.get_response(request)

        # Skip if user is not authenticated
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return self.get_response(request)

        workspace_id = request.headers.get("X-Workspace-ID")
        if workspace_id:
            try:
                from apps.workspaces.models import Workspace

                workspace = Workspace.objects.filter(
                    id=workspace_id,
                    memberships__user=request.user,
                    is_active=True,
                ).first()

                if workspace is None:
                    return JsonResponse(
                        {"detail": "Workspace not found or access denied."},
                        status=403,
                    )

                request.workspace = workspace  # type: ignore[attr-defined]
            except (ValueError, TypeError):
                return JsonResponse(
                    {"detail": "Invalid Workspace ID."},
                    status=400,
                )

        return self.get_response(request)
