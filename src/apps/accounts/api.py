"""
PayloadOps — Accounts API Endpoints

Authentication (register, login, refresh) and API key management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
from django.contrib.auth import authenticate
from ninja import Router

from apps.accounts.auth import (
    JWTAuth,
    auth,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from apps.accounts.models import APIKey, User
from apps.accounts.schemas import (
    APIKeyCreatedOutput,
    APIKeyCreateInput,
    APIKeyOutput,
    LoginInput,
    MessageOutput,
    RefreshInput,
    RegisterInput,
    TokenOutput,
    UserOutput,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

router = Router()


# ==========================================
# Authentication
# ==========================================


@router.post("/register", response={201: UserOutput, 400: MessageOutput})
def register(request: HttpRequest, payload: RegisterInput):
    """Register a new user account."""
    if User.objects.filter(email=payload.email).exists():
        return 400, {"detail": "A user with this email already exists."}

    if User.objects.filter(username=payload.username).exists():
        return 400, {"detail": "A user with this username already exists."}

    user = User.objects.create_user(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
    )
    return 201, user


@router.post("/login", response={200: TokenOutput, 401: MessageOutput})
def login(request: HttpRequest, payload: LoginInput):
    """Login and receive JWT access and refresh tokens."""
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is None:
        return 401, {"detail": "Invalid email or password."}

    access_token, expires_in = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return 200, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@router.post("/refresh", response={200: TokenOutput, 401: MessageOutput})
def refresh(request: HttpRequest, payload: RefreshInput):
    """Refresh an access token using a valid refresh token."""
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            return 401, {"detail": "Invalid token type."}

        user = User.objects.filter(id=token_data["sub"], is_active=True).first()
        if user is None:
            return 401, {"detail": "User not found."}

        access_token, expires_in = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        return 200, {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return 401, {"detail": "Invalid or expired refresh token."}


@router.get("/me", auth=JWTAuth(), response=UserOutput)
def me(request: HttpRequest):
    """Get the current authenticated user's profile."""
    return request.auth


# ==========================================
# API Keys
# ==========================================


@router.post("/api-keys", auth=auth, response={201: APIKeyCreatedOutput, 400: MessageOutput})
def create_api_key(request: HttpRequest, payload: APIKeyCreateInput):
    """Create a new API key for the current workspace."""
    workspace = getattr(request, "workspace", None)
    if workspace is None:
        return 400, {"detail": "X-Workspace-ID header is required."}

    full_key, prefix, hashed = APIKey.generate_key(is_test=payload.is_test)

    api_key = APIKey.objects.create(
        name=payload.name,
        prefix=prefix,
        hashed_key=hashed,
        user=request.auth,
        workspace=workspace,
    )

    return 201, {
        "id": api_key.id,
        "name": api_key.name,
        "prefix": api_key.prefix,
        "key": full_key,
        "is_active": api_key.is_active,
        "last_used_at": api_key.last_used_at,
        "expires_at": api_key.expires_at,
        "created_at": api_key.created_at,
    }


@router.get("/api-keys", auth=auth, response=list[APIKeyOutput])
def list_api_keys(request: HttpRequest):
    """List all API keys for the current workspace."""
    workspace = getattr(request, "workspace", None)
    if workspace is None:
        return []
    return APIKey.objects.filter(workspace=workspace, user=request.auth)


@router.delete("/api-keys/{key_id}", auth=auth, response={200: MessageOutput, 404: MessageOutput})
def revoke_api_key(request: HttpRequest, key_id: str):
    """Revoke (deactivate) an API key."""
    api_key = APIKey.objects.filter(
        id=key_id,
        user=request.auth,
    ).first()

    if api_key is None:
        return 404, {"detail": "API key not found."}

    api_key.is_active = False
    api_key.save(update_fields=["is_active"])
    return 200, {"detail": "API key revoked successfully."}
