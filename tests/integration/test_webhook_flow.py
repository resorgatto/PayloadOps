"""
PayloadOps — Integration Tests: Webhook Flow

End-to-end tests for the webhook ingestion and processing pipeline.
"""

from __future__ import annotations

import pytest
from django.test import Client

from apps.observability.models import ExecutionLog
from apps.workflows.models import Action, Trigger, Workflow


@pytest.mark.django_db
@pytest.mark.integration
class TestWebhookIngestion:
    """Test the webhook ingestion endpoint."""

    def test_valid_webhook_returns_202(self, workspace, client: Client):
        """A valid POST to a webhook URL should return 202 Accepted."""
        workflow = Workflow.objects.create(
            workspace=workspace,
            name="Test Workflow",
            status=Workflow.Status.ACTIVE,
        )
        trigger = Trigger.objects.create(workspace=workspace, workflow=workflow)
        Action.objects.create(
            workspace=workspace,
            workflow=workflow,
            name="Test Action",
            url="https://httpbin.org/post",
        )

        response = client.post(
            f"/api/workflows/hooks/{trigger.webhook_path}",
            data={"name": "Test Lead", "email": "lead@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "execution_id" in data

    def test_unknown_webhook_returns_404(self, client: Client):
        """A POST to a non-existent webhook should return 404."""
        response = client.post(
            "/api/workflows/hooks/00000000-0000-0000-0000-000000000000",
            data={"test": True},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_inactive_workflow_returns_422(self, workspace, client: Client):
        """A POST to a webhook with an inactive workflow should return 422."""
        workflow = Workflow.objects.create(
            workspace=workspace,
            name="Draft Workflow",
            status=Workflow.Status.DRAFT,
        )
        trigger = Trigger.objects.create(workspace=workspace, workflow=workflow)

        response = client.post(
            f"/api/workflows/hooks/{trigger.webhook_path}",
            data={"test": True},
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_execution_log_created(self, workspace, client: Client):
        """Webhook ingestion should create an ExecutionLog entry."""
        workflow = Workflow.objects.create(
            workspace=workspace,
            name="Log Test Workflow",
            status=Workflow.Status.ACTIVE,
        )
        trigger = Trigger.objects.create(workspace=workspace, workflow=workflow)

        payload = {"name": "Test", "email": "test@test.com"}
        client.post(
            f"/api/workflows/hooks/{trigger.webhook_path}",
            data=payload,
            content_type="application/json",
        )

        log = ExecutionLog.objects.filter(workflow=workflow).first()
        assert log is not None
        assert log.status == ExecutionLog.Status.PENDING
        assert log.payload_received == payload
