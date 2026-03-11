"""
SEAM — Unit Tests: Models

Tests for core model behavior, validation, and business logic.
"""

from __future__ import annotations

import pytest
from django.db import IntegrityError

from apps.accounts.models import APIKey, User
from apps.observability.models import ExecutionLog
from apps.workflows.models import Action, Credential, Trigger, Workflow
from apps.workspaces.models import Workspace, WorkspaceMembership


# ==========================================
# User Model Tests
# ==========================================


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, user):
        assert user.email == "test@seam.dev"
        assert user.username == "testuser"
        assert user.check_password("testpass123")

    def test_unique_email(self, user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test@seam.dev",
                username="another",
                password="pass",
            )


# ==========================================
# Workspace Model Tests
# ==========================================


@pytest.mark.django_db
class TestWorkspaceModel:
    def test_create_workspace(self, workspace):
        assert workspace.name == "Test Workspace"
        assert workspace.slug == "test-workspace"
        assert workspace.is_active is True

    def test_auto_slug_generation(self, db):
        ws = Workspace.objects.create(name="My New Workspace")
        assert ws.slug == "my-new-workspace"

    def test_membership_roles(self, workspace, user):
        membership = WorkspaceMembership.objects.get(workspace=workspace, user=user)
        assert membership.role == WorkspaceMembership.Role.OWNER


# ==========================================
# API Key Model Tests
# ==========================================


@pytest.mark.django_db
class TestAPIKeyModel:
    def test_generate_key(self):
        full_key, prefix, hashed = APIKey.generate_key()
        assert full_key.startswith("po_live_")
        assert prefix == "po_live_"
        assert len(hashed) == 64  # SHA-256 hex digest

    def test_generate_test_key(self):
        full_key, prefix, hashed = APIKey.generate_key(is_test=True)
        assert full_key.startswith("po_test_")

    def test_hash_key_consistency(self):
        full_key, _, expected_hash = APIKey.generate_key()
        assert APIKey.hash_key(full_key) == expected_hash


# ==========================================
# Workflow Model Tests
# ==========================================


@pytest.mark.django_db
class TestWorkflowModel:
    def test_create_workflow(self, workspace):
        wf = Workflow.objects.create(
            workspace=workspace,
            name="Test Workflow",
            description="A test workflow",
        )
        assert wf.status == Workflow.Status.DRAFT
        assert wf.is_active is False

    def test_activate_workflow(self, workspace):
        wf = Workflow.objects.create(
            workspace=workspace,
            name="Active Workflow",
            status=Workflow.Status.ACTIVE,
        )
        assert wf.is_active is True

    def test_trigger_generation(self, workspace):
        wf = Workflow.objects.create(workspace=workspace, name="Triggered WF")
        trigger = Trigger.objects.create(workspace=workspace, workflow=wf)
        assert trigger.webhook_path is not None
        assert trigger.webhook_url.startswith("/hooks/")

    def test_action_ordering(self, workspace):
        wf = Workflow.objects.create(workspace=workspace, name="Multi-Action WF")
        a2 = Action.objects.create(workspace=workspace, workflow=wf, name="Second", order=2, url="https://example.com/2")
        a1 = Action.objects.create(workspace=workspace, workflow=wf, name="First", order=1, url="https://example.com/1")
        actions = list(Action.objects.filter(workflow=wf).order_by("order"))
        assert actions[0].name == "First"
        assert actions[1].name == "Second"


# ==========================================
# Tenant Isolation Tests
# ==========================================


@pytest.mark.django_db
class TestTenantIsolation:
    def test_workflow_isolation(self, workspace, second_workspace):
        wf1 = Workflow.objects.create(workspace=workspace, name="WF-1")
        wf2 = Workflow.objects.create(workspace=second_workspace, name="WF-2")

        # Workspace 1 should only see WF-1
        ws1_workflows = Workflow.objects.for_workspace(workspace)
        assert ws1_workflows.count() == 1
        assert ws1_workflows.first().name == "WF-1"

        # Workspace 2 should only see WF-2
        ws2_workflows = Workflow.objects.for_workspace(second_workspace)
        assert ws2_workflows.count() == 1
        assert ws2_workflows.first().name == "WF-2"

    def test_execution_log_isolation(self, workspace, second_workspace):
        wf1 = Workflow.objects.create(workspace=workspace, name="WF-1")
        wf2 = Workflow.objects.create(workspace=second_workspace, name="WF-2")

        ExecutionLog.objects.create(workspace=workspace, workflow=wf1, payload_received={"test": 1})
        ExecutionLog.objects.create(workspace=second_workspace, workflow=wf2, payload_received={"test": 2})

        ws1_logs = ExecutionLog.objects.for_workspace(workspace)
        assert ws1_logs.count() == 1
        assert ws1_logs.first().payload_received == {"test": 1}


# ==========================================
# Credential Encryption Tests
# ==========================================


@pytest.mark.django_db
class TestCredentialEncryption:
    def test_encrypt_decrypt(self, workspace):
        cred = Credential(workspace=workspace, name="Test Token")
        cred.set_value("my-secret-token-12345")
        cred.save()

        # Value should be encrypted in DB
        cred.refresh_from_db()
        assert cred.encrypted_value != "my-secret-token-12345"

        # Should decrypt correctly
        assert cred.get_value() == "my-secret-token-12345"
