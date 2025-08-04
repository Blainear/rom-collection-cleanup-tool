"""
Simple credential management for ROM cleanup tool.

This module provides basic storage and retrieval of API credentials
using JSON file storage.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Service name for credentials
SERVICE_NAME = "rom-cleanup-tool"
CONFIG_DIR = Path.home() / ".rom-cleanup-tool"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


class CredentialManager:
    """Manages storage and retrieval of API credentials."""

    def __init__(self) -> None:
        """Initialize the credential manager."""
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(exist_ok=True)

    def store_credential(self, key: str, value: str) -> bool:
        """Store a credential.

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
            # Load existing credentials
            credentials = self._load_credentials()

            # Store the new credential
            credentials[key] = value

            # Save back to file
            with open(CREDENTIALS_FILE, "w") as f:
                json.dump(credentials, f, indent=2)

            # Set restrictive permissions
            os.chmod(CREDENTIALS_FILE, 0o600)

            logger.debug(f"Stored credential {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing credential {key}: {e}")
            return False

    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve a credential.

        Args:
            key: Credential identifier

        Returns:
            The credential value or None if not found
        """
        try:
            credentials = self._load_credentials()
            return credentials.get(key)

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
            credentials = self._load_credentials()

            if key in credentials:
                del credentials[key]

                if credentials:
                    # Save updated credentials
                    with open(CREDENTIALS_FILE, "w") as f:
                        json.dump(credentials, f, indent=2)
                    os.chmod(CREDENTIALS_FILE, 0o600)
                else:
                    # Remove file if no credentials left
                    if CREDENTIALS_FILE.exists():
                        CREDENTIALS_FILE.unlink()

                logger.debug(f"Deleted credential {key}")
                return True

            return True  # Not found, but that's fine

        except Exception as e:
            logger.error(f"Error deleting credential {key}: {e}")
            return False

    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from JSON file."""
        try:
            if CREDENTIALS_FILE.exists():
                with open(CREDENTIALS_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
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

        # Also remove credential file
        try:
            if CREDENTIALS_FILE.exists():
                CREDENTIALS_FILE.unlink()
        except Exception as e:
            logger.error(f"Error removing credential file: {e}")
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
