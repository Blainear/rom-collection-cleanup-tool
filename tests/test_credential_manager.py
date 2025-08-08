"""Tests for credential manager module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from credential_manager import (
    CredentialManager,
    _reset_credential_manager,
    get_credential_manager,
)


class TestCredentialManager(unittest.TestCase):
    """Test cases for CredentialManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".rom-cleanup-tool"

        # Mock the _get_config_dir function to return our test directory
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            self.manager = CredentialManager()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        _reset_credential_manager()

    def test_init_creates_config_directory(self):
        """Test that initialization creates config directory."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()
            self.assertIsNotNone(manager)
            # The directory should be created during initialization
            self.assertTrue(self.config_dir.exists())

    def test_store_credential(self):
        """Test storing credential."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            result = manager.store_credential("test_key", "test_value")

            self.assertTrue(result)
            # Check that credential was stored
            stored_value = manager.get_credential("test_key")
            self.assertEqual(stored_value, "test_value")

    def test_get_credential(self):
        """Test retrieving credential."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            # Store a credential first
            manager.store_credential("test_key", "test_value")

            # Retrieve it
            result = manager.get_credential("test_key")

            self.assertEqual(result, "test_value")

    def test_delete_credential(self):
        """Test deleting credential."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            # Store a credential first
            manager.store_credential("test_key", "test_value")

            # Delete it
            result = manager.delete_credential("test_key")

            self.assertTrue(result)
            # Check that credential was deleted
            stored_value = manager.get_credential("test_key")
            self.assertIsNone(stored_value)

    def test_store_empty_credential_fails(self):
        """Test that storing empty credentials fails."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            result = manager.store_credential("test_key", "")
            self.assertFalse(result)

            result = manager.store_credential("test_key", "   ")
            self.assertFalse(result)

    def test_get_nonexistent_credential_returns_none(self):
        """Test that getting nonexistent credential returns None."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            result = manager.get_credential("nonexistent_key")
            self.assertIsNone(result)

    def test_list_stored_credentials(self):
        """Test listing stored credentials."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            # Store some credentials
            manager.store_credential("tgdb_api_key", "test_tgdb_key")
            manager.store_credential("igdb_client_id", "test_igdb_id")

            # List credentials
            credentials = manager.list_stored_credentials()

            self.assertTrue(credentials["tgdb_api_key"])
            self.assertTrue(credentials["igdb_client_id"])
            self.assertFalse(credentials["igdb_access_token"])

    def test_clear_all_credentials(self):
        """Test clearing all credentials."""
        with patch("credential_manager._get_config_dir") as mock_get_config:
            mock_get_config.return_value = self.config_dir
            manager = CredentialManager()

            # Store some credentials
            manager.store_credential("tgdb_api_key", "test_tgdb_key")
            manager.store_credential("igdb_client_id", "test_igdb_id")

            # Clear all credentials
            result = manager.clear_all_credentials()

            self.assertTrue(result)
            # Check that credentials were cleared
            credentials = manager.list_stored_credentials()
            self.assertFalse(credentials["tgdb_api_key"])
            self.assertFalse(credentials["igdb_client_id"])

    def test_ci_environment_uses_temp_directory(self):
        """Ensure CI environments use a temp directory for config."""
        with patch.dict(os.environ, {"CI": "true"}):
            manager = CredentialManager()
            self.assertIn("rom-cleanup-test-", manager.config_dir.parent.name)
            import shutil

            shutil.rmtree(manager.config_dir.parent, ignore_errors=True)


class TestCredentialManagerSingleton(unittest.TestCase):
    """Test cases for credential manager singleton pattern."""

    def setUp(self):
        """Set up test fixtures."""
        _reset_credential_manager()

    def tearDown(self):
        """Clean up test fixtures."""
        _reset_credential_manager()

    def test_get_credential_manager_returns_same_instance(self):
        """Test that get_credential_manager returns the same instance."""
        manager1 = get_credential_manager()
        manager2 = get_credential_manager()

        self.assertIs(manager1, manager2)

    def test_get_credential_manager_returns_credential_manager(self):
        """Test that get_credential_manager returns CredentialManager instance."""
        manager = get_credential_manager()
        self.assertIsInstance(manager, CredentialManager)


if __name__ == "__main__":
    unittest.main()
