"""
SEAM — Django Ninja API Router

Central API configuration with versioning and all app routers.
"""

from ninja import NinjaAPI

from apps.accounts.api import router as accounts_router
from apps.observability.api import router as observability_router
from apps.workflows.api import router as workflows_router
from apps.workspaces.api import router as workspaces_router

api = NinjaAPI(
    title="SEAM API",
    version="1.0.0",
    description=(
        "SEAM is a multi-tenant SaaS webhook integration hub. "
        "Connect systems through configurable workflows that receive, "
        "process, and forward data between services."
    ),
    urls_namespace="api",
)

# Register app routers
api.add_router("/auth/", accounts_router, tags=["Authentication"])
api.add_router("/workspaces/", workspaces_router, tags=["Workspaces"])
api.add_router("/workflows/", workflows_router, tags=["Workflows"])
api.add_router("/logs/", observability_router, tags=["Observability"])
