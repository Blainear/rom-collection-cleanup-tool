"""
Secure credential management for ROM cleanup tool.

This module provides secure storage and retrieval of API credentials
using the keyring library with fallback to encrypted local storage.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

try:
    from cryptography.fernet import Fernet

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Service name for keyring
SERVICE_NAME = "rom-cleanup-tool"
CONFIG_DIR = Path.home() / ".rom-cleanup-tool"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.enc"
KEY_FILE = CONFIG_DIR / "key.key"


class CredentialManager:
    """Manages secure storage and retrieval of API credentials."""

    def __init__(self) -> None:
        """Initialize the credential manager."""
        self.keyring_available = KEYRING_AVAILABLE
        self.crypto_available = CRYPTOGRAPHY_AVAILABLE
        self._encryption_key: Optional[bytes] = None

        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(exist_ok=True)

        if not self.keyring_available:
            logger.warning(
                "Keyring not available, falling back to encrypted local storage"
            )
            if not self.crypto_available:
                logger.error(
                    "Neither keyring nor cryptography available - credentials will not be secure!"
                )

    def _get_encryption_key(self) -> Optional[bytes]:
        """Get or create encryption key for local storage."""
        if not self.crypto_available:
            return None

        if self._encryption_key is not None:
            return self._encryption_key

        try:
            # Use the config directory for the key file
            key_file = CONFIG_DIR / "key.key"
            
            if key_file.exists():
                # Load existing key
                with open(key_file, "rb") as f:
                    self._encryption_key = f.read()
            else:
                # Generate new key
                self._encryption_key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(self._encryption_key)
                # Set restrictive permissions
                os.chmod(key_file, 0o600)

            return self._encryption_key
        except Exception as e:
            logger.error(f"Error managing encryption key: {e}")
            return None

    def store_credential(self, key: str, value: str) -> bool:
        """Store a credential securely.

        Args:
            key: Credential identifier
            value: Credential value to store

        Returns:
            True if stored successfully, False otherwise
        """
        if not value or not value.strip():
            logger.warning(f"Attempted to store empty credential for {key}")
            return False

        try:
            # Try keyring first
            if self.keyring_available:
                keyring.set_password(SERVICE_NAME, key, value)
                logger.debug(f"Stored credential {key} in keyring")
                return True

            # Fallback to encrypted local storage
            return self._store_credential_local(key, value)

        except Exception as e:
            logger.error(f"Error storing credential {key}: {e}")
            return False

    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve a credential securely.

        Args:
            key: Credential identifier

        Returns:
            The credential value or None if not found
        """
        try:
            # Try keyring first
            if self.keyring_available:
                value = keyring.get_password(SERVICE_NAME, key)
                if value:
                    return value

            # Fallback to local storage
            return self._get_credential_local(key)

        except Exception as e:
            logger.error(f"Error retrieving credential {key}: {e}")
            return None

    def delete_credential(self, key: str) -> bool:
        """Delete a stored credential.

        Args:
            key: Credential identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Try keyring first
            if self.keyring_available:
                try:
                    keyring.delete_password(SERVICE_NAME, key)
                    logger.debug(f"Deleted credential {key} from keyring")
                except keyring.errors.PasswordDeleteError:
                    pass  # Credential wasn't in keyring

            # Also try local storage
            return self._delete_credential_local(key)

        except Exception as e:
            logger.error(f"Error deleting credential {key}: {e}")
            return False

    def _store_credential_local(self, key: str, value: str) -> bool:
        """Store credential in encrypted local file."""
        if not self.crypto_available:
            logger.error("Cannot store credential locally - cryptography not available")
            return False

        encryption_key = self._get_encryption_key()
        if not encryption_key:
            logger.error("Cannot get encryption key for local storage")
            return False

        try:
            # Load existing credentials
            credentials = self._load_credentials_local()

            # Encrypt and store the new credential
            fernet = Fernet(encryption_key)
            encrypted_value = fernet.encrypt(value.encode())
            credentials[key] = base64.b64encode(encrypted_value).decode()

            # Save back to file
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f)

            # Set restrictive permissions
            os.chmod(CREDENTIALS_FILE, 0o600)

            logger.debug(f"Stored credential {key} in local encrypted storage")
            return True

        except Exception as e:
            logger.error(f"Error storing credential locally: {e}")
            return False

    def _get_credential_local(self, key: str) -> Optional[str]:
        """Get credential from encrypted local file."""
        if not self.crypto_available:
            return None

        encryption_key = self._get_encryption_key()
        if not encryption_key:
            return None

        try:
            credentials = self._load_credentials_local()
            encrypted_value = credentials.get(key)

            if not encrypted_value:
                return None

            # Decrypt the value
            fernet = Fernet(encryption_key)
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted_value = fernet.decrypt(encrypted_bytes).decode()

            return decrypted_value

        except Exception as e:
            logger.error(f"Error retrieving credential from local storage: {e}")
            return None

    def _delete_credential_local(self, key: str) -> bool:
        """Delete credential from local encrypted file."""
        try:
            credentials = self._load_credentials_local()

            if key in credentials:
                del credentials[key]

                if credentials:
                    # Save updated credentials
                    with open(CREDENTIALS_FILE, "w") as f:
                        json.dump(credentials, f)
                    os.chmod(CREDENTIALS_FILE, 0o600)
                else:
                    # Remove file if no credentials left
                    if CREDENTIALS_FILE.exists():
                        CREDENTIALS_FILE.unlink()

                logger.debug(f"Deleted credential {key} from local storage")
                return True

            return True  # Not found, but that's fine

        except Exception as e:
            logger.error(f"Error deleting credential from local storage: {e}")
            return False

    def _load_credentials_local(self) -> Dict[str, Any]:
        """Load credentials from local encrypted file."""
        try:
            if CREDENTIALS_FILE.exists():
                with open(CREDENTIALS_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading local credentials: {e}")
            return {}

    def list_stored_credentials(self) -> Dict[str, bool]:
        """List which credentials are stored.

        Returns:
            Dictionary mapping credential keys to whether they exist
        """
        credentials = {}
        common_keys = ["tgdb_api_key", "igdb_client_id", "igdb_access_token"]

        for key in common_keys:
            try:
                value = self.get_credential(key)
                credentials[key] = bool(value and value.strip())
            except Exception as e:
                logger.error(f"Error checking credential {key}: {e}")
                credentials[key] = False

        return credentials

    def clear_all_credentials(self) -> bool:
        """Clear all stored credentials.

        Returns:
            True if all credentials cleared successfully
        """
        success = True
        common_keys = ["tgdb_api_key", "igdb_client_id", "igdb_access_token"]

        for key in common_keys:
            if not self.delete_credential(key):
                success = False

        # Also remove local files
        try:
            if CREDENTIALS_FILE.exists():
                CREDENTIALS_FILE.unlink()
            if KEY_FILE.exists():
                KEY_FILE.unlink()
        except Exception as e:
            logger.error(f"Error removing credential files: {e}")
            success = False

        return success


# Global instance
_credential_manager = None


def get_credential_manager() -> CredentialManager:
    """Get the global credential manager instance."""
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager
