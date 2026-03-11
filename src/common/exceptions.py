"""
PayloadOps — Custom API Exceptions
"""

from __future__ import annotations


class PayloadOpsError(Exception):
    """Base exception for PayloadOps."""

    def __init__(self, message: str = "An error occurred", status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WorkspaceNotFoundError(PayloadOpsError):
    """Raised when the workspace cannot be found or user has no access."""

    def __init__(self, message: str = "Workspace not found or access denied") -> None:
        super().__init__(message=message, status_code=403)


class WebhookNotFoundError(PayloadOpsError):
    """Raised when a webhook trigger path is not found."""

    def __init__(self, message: str = "Webhook not found") -> None:
        super().__init__(message=message, status_code=404)


class WorkflowInactiveError(PayloadOpsError):
    """Raised when attempting to trigger an inactive workflow."""

    def __init__(self, message: str = "Workflow is not active") -> None:
        super().__init__(message=message, status_code=422)


class EncryptionError(PayloadOpsError):
    """Raised when encryption/decryption fails."""

    def __init__(self, message: str = "Encryption error") -> None:
        super().__init__(message=message, status_code=500)
