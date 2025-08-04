"""Tests for credential manager module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from credential_manager import CredentialManager, get_credential_manager


class TestCredentialManager(unittest.TestCase):
    """Test cases for CredentialManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".rom-cleanup-tool"

        # Mock the config directory
        with patch("credential_manager.CONFIG_DIR", self.config_dir):
            self.manager = CredentialManager()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_config_directory(self):
        """Test that initialization creates config directory."""
        with patch("credential_manager.CONFIG_DIR", self.config_dir):
            manager = CredentialManager()
            self.assertIsNotNone(
                manager
            )  # Manager creation triggers directory creation
            self.assertTrue(self.config_dir.exists())

    @patch("credential_manager.KEYRING_AVAILABLE", True)
    @patch("keyring.set_password")
    def test_store_credential_with_keyring(self, mock_set_password):
        """Test storing credential using keyring."""
        mock_set_password.return_value = None

        result = self.manager.store_credential("test_key", "test_value")

        self.assertTrue(result)
        mock_set_password.assert_called_once_with(
            "rom-cleanup-tool", "test_key", "test_value"
        )

    @patch("credential_manager.KEYRING_AVAILABLE", True)
    @patch("keyring.get_password")
    def test_get_credential_with_keyring(self, mock_get_password):
        """Test retrieving credential using keyring."""
        mock_get_password.return_value = "test_value"

        result = self.manager.get_credential("test_key")

        self.assertEqual(result, "test_value")
        mock_get_password.assert_called_once_with("rom-cleanup-tool", "test_key")

    @patch("credential_manager.KEYRING_AVAILABLE", True)
    @patch("keyring.delete_password")
    def test_delete_credential_with_keyring(self, mock_delete_password):
        """Test deleting credential using keyring."""
        mock_delete_password.return_value = None

        result = self.manager.delete_credential("test_key")

        self.assertTrue(result)
        mock_delete_password.assert_called_once_with("rom-cleanup-tool", "test_key")

    @patch("credential_manager.KEYRING_AVAILABLE", False)
    @patch("credential_manager.CRYPTOGRAPHY_AVAILABLE", True)
    def test_store_credential_local_fallback(self):
        """Test storing credential using local encrypted storage."""
        # Skip if cryptography is not available
        try:
            import cryptography.fernet  # noqa: F401
        except ImportError:
            self.skipTest("cryptography not available")

        # Mock the cryptography.fernet module at the import level
        with patch("cryptography.fernet.Fernet") as mock_fernet:
            # Mock Fernet.generate_key and Fernet instance
            mock_fernet.generate_key.return_value = b"test_key_32_bytes_long_for_fernet"
            mock_fernet_instance = Mock()
            mock_fernet_instance.encrypt.return_value = b"encrypted_data"
            mock_fernet.return_value = mock_fernet_instance

            with patch("credential_manager.CONFIG_DIR", self.config_dir):
                manager = CredentialManager()

                result = manager.store_credential("test_key", "test_value")

                self.assertTrue(result)
                # Check that files were created
                credentials_file = self.config_dir / "credentials.enc"
                key_file = self.config_dir / "key.key"
                self.assertTrue(credentials_file.exists())
                self.assertTrue(key_file.exists())

    @patch("credential_manager.KEYRING_AVAILABLE", False)
    @patch("credential_manager.CRYPTOGRAPHY_AVAILABLE", True)
    def test_get_credential_local_fallback(self):
        """Test retrieving credential using local encrypted storage."""
        # Skip if cryptography is not available
        try:
            import cryptography.fernet  # noqa: F401
        except ImportError:
            self.skipTest("cryptography not available")

        # Mock the cryptography.fernet module at the import level
        with patch("cryptography.fernet.Fernet") as mock_fernet:
            # Mock Fernet.generate_key and Fernet instance
            mock_fernet.generate_key.return_value = b"test_key_32_bytes_long_for_fernet"
            mock_fernet_instance = Mock()
            mock_fernet_instance.encrypt.return_value = b"encrypted_data"
            mock_fernet_instance.decrypt.return_value = b"test_value"
            mock_fernet.return_value = mock_fernet_instance

            with patch("credential_manager.CONFIG_DIR", self.config_dir):
                manager = CredentialManager()

                # Store first
                manager.store_credential("test_key", "test_value")

                # Then retrieve
                result = manager.get_credential("test_key")

                self.assertEqual(result, "test_value")

    def test_store_empty_credential_fails(self):
        """Test that storing empty credential fails."""
        result = self.manager.store_credential("test_key", "")
        self.assertFalse(result)

        result = self.manager.store_credential("test_key", "   ")
        self.assertFalse(result)

    def test_get_nonexistent_credential_returns_none(self):
        """Test that getting nonexistent credential returns None."""
        result = self.manager.get_credential("nonexistent_key")
        self.assertIsNone(result)

    @patch("credential_manager.KEYRING_AVAILABLE", False)
    @patch("credential_manager.CRYPTOGRAPHY_AVAILABLE", False)
    def test_no_security_libraries_available(self):
        """Test behavior when no security libraries are available."""
        with patch("credential_manager.CONFIG_DIR", self.config_dir):
            manager = CredentialManager()

            # Should still work but warn about lack of security
            result = manager.store_credential("test_key", "test_value")
            self.assertFalse(result)  # Should fail without crypto

    def test_list_stored_credentials(self):
        """Test listing stored credentials."""
        # Mock successful retrieval for some credentials
        with patch.object(self.manager, "get_credential") as mock_get:
            mock_get.side_effect = lambda key: {
                "tgdb_api_key": "api_key_value",
                "igdb_client_id": "client_id_value",
                "igdb_access_token": None,
            }.get(key)

            result = self.manager.list_stored_credentials()

            expected = {
                "tgdb_api_key": True,
                "igdb_client_id": True,
                "igdb_access_token": False,
            }
            self.assertEqual(result, expected)

    def test_clear_all_credentials(self):
        """Test clearing all credentials."""
        with patch.object(self.manager, "delete_credential") as mock_delete:
            mock_delete.return_value = True

            result = self.manager.clear_all_credentials()

            self.assertTrue(result)
            # Should have called delete for each common key
            self.assertEqual(mock_delete.call_count, 3)


class TestCredentialManagerSingleton(unittest.TestCase):
    """Test the global credential manager singleton."""

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
