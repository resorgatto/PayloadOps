"""
PayloadOps — Encryption Utilities

Provides Fernet symmetric encryption for storing sensitive data
such as API credentials and tokens in the database.
"""

from __future__ import annotations

import base64
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_fernet() -> Fernet:
    """Get a Fernet instance using the configured encryption key."""
    key = settings.ENCRYPTION_KEY
    # Ensure the key is valid base64-encoded 32-byte key
    try:
        Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, Exception):
        # If key is not valid Fernet key, derive one from the provided key
        key_bytes = key.encode() if isinstance(key, str) else key
        key = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32]).decode()

    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a plaintext string and return the encrypted value as a string.

    Args:
        plaintext: The string to encrypt.

    Returns:
        The encrypted string (base64 encoded).
    """
    f = _get_fernet()
    encrypted = f.encrypt(plaintext.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_value(encrypted_text: str) -> str:
    """
    Decrypt an encrypted string and return the plaintext.

    Args:
        encrypted_text: The encrypted string to decrypt.

    Returns:
        The decrypted plaintext string.

    Raises:
        InvalidToken: If the encrypted text is invalid or corrupted.
    """
    f = _get_fernet()
    try:
        decrypted = f.decrypt(encrypted_text.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        logger.error("Failed to decrypt value — invalid token or corrupted data")
        raise
