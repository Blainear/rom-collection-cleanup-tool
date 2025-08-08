"""
Simple credential management for ROM cleanup tool.

This module provides basic storage and retrieval of API credentials
using UTF-8 encoded JSON file storage to ensure consistent behavior
across platforms.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Service name for credentials
SERVICE_NAME = "rom-cleanup-tool"


def _get_config_dir() -> Path:
    """Get the config directory, with fallback for CI environments."""
    # Check if we're in a CI environment
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        # Use a temporary directory for CI
        import tempfile

        temp_dir = tempfile.mkdtemp(prefix="rom-cleanup-test-")
        return Path(temp_dir) / ".rom-cleanup-tool"
    return Path.home() / ".rom-cleanup-tool"


class CredentialManager:
    """Manages storage and retrieval of API credentials."""

    def __init__(self) -> None:
        """Initialize the credential manager."""
        # Resolve paths at runtime so tests can patch directory logic
        self.config_dir = _get_config_dir()
        self.credentials_file = self.config_dir / "credentials.json"

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

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
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                json.dump(credentials, f, indent=2)

            # Set restrictive permissions (skip on Windows)
            try:
                os.chmod(self.credentials_file, 0o600)
            except (OSError, NotImplementedError):
                # Skip on Windows or if not supported
                pass

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
                    with open(self.credentials_file, "w", encoding="utf-8") as f:
                        json.dump(credentials, f, indent=2)
                    # Set restrictive permissions (skip on Windows)
                    try:
                        os.chmod(self.credentials_file, 0o600)
                    except (OSError, NotImplementedError):
                        # Skip on Windows or if not supported
                        pass
                else:
                    # Remove file if no credentials left
                    if self.credentials_file.exists():
                        self.credentials_file.unlink()

                logger.debug(f"Deleted credential {key}")
                return True

            return True  # Not found, but that's fine

        except Exception as e:
            logger.error(f"Error deleting credential {key}: {e}")
            return False

    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from JSON file."""
        try:
            if self.credentials_file.exists():
                with open(self.credentials_file, "r", encoding="utf-8") as f:
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
            if self.credentials_file.exists():
                self.credentials_file.unlink()
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


# Reset function for testing
def _reset_credential_manager():
    """Reset the global credential manager instance (for testing)."""
    global _credential_manager
    _credential_manager = None
