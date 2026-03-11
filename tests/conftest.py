"""
PayloadOps — Test Configuration

Shared pytest fixtures and test utilities.
"""

from __future__ import annotations

import uuid

import pytest
from django.test import RequestFactory

from apps.accounts.models import User
from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.fixture
def request_factory():
    """Django request factory."""
    return RequestFactory()


@pytest.fixture
def user(db) -> User:
    """Create a test user."""
    return User.objects.create_user(
        email="test@payloadops.dev",
        username="testuser",
        password="testpass123",
        full_name="Test User",
    )


@pytest.fixture
def workspace(db, user) -> Workspace:
    """Create a test workspace with the user as owner."""
    ws = Workspace.objects.create(
        name="Test Workspace",
        slug="test-workspace",
        description="A test workspace",
    )
    WorkspaceMembership.objects.create(
        user=user,
        workspace=ws,
        role=WorkspaceMembership.Role.OWNER,
    )
    return ws


@pytest.fixture
def second_user(db) -> User:
    """Create a second test user."""
    return User.objects.create_user(
        email="second@payloadops.dev",
        username="seconduser",
        password="testpass123",
        full_name="Second User",
    )


@pytest.fixture
def second_workspace(db, second_user) -> Workspace:
    """Create a second workspace (for tenant isolation tests)."""
    ws = Workspace.objects.create(
        name="Other Workspace",
        slug="other-workspace",
    )
    WorkspaceMembership.objects.create(
        user=second_user,
        workspace=ws,
        role=WorkspaceMembership.Role.OWNER,
    )
    return ws
