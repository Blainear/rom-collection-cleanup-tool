# Service name for credentials
SERVICE_NAME = "rom-cleanup-tool"
CONFIG_DIR = Path.home() / ".rom-cleanup-tool"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"


class CredentialManager:
    """Manages storage and retrieval of API credentials."""

    def __init__(self) -> None:
        """Initialize the credential manager."""
        # Resolve paths at runtime so tests can patch CONFIG_DIR
        self.config_dir = CONFIG_DIR
        self.credentials_file = self.config_dir / "credentials.json"

        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def store_credential(self, key: str, value: str) -> bool:
        """Store a credential.
@@ -49,12 +52,12 @@ def store_credential(self, key: str, value: str) -> bool:
            credentials[key] = value

            # Save back to file
            with open(CREDENTIALS_FILE, "w") as f:
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f, indent=2)

            # Set restrictive permissions (skip on Windows)
            try:
                os.chmod(CREDENTIALS_FILE, 0o600)
                os.chmod(self.credentials_file, 0o600)
            except (OSError, NotImplementedError):
                # Skip on Windows or if not supported
                pass
@@ -100,18 +103,18 @@ def delete_credential(self, key: str) -> bool:

                if credentials:
                    # Save updated credentials
                    with open(CREDENTIALS_FILE, "w") as f:
                    with open(self.credentials_file, "w") as f:
                        json.dump(credentials, f, indent=2)
                    # Set restrictive permissions (skip on Windows)
                    try:
                        os.chmod(CREDENTIALS_FILE, 0o600)
                        os.chmod(self.credentials_file, 0o600)
                    except (OSError, NotImplementedError):
                        # Skip on Windows or if not supported
                        pass
                else:
                    # Remove file if no credentials left
                    if CREDENTIALS_FILE.exists():
                        CREDENTIALS_FILE.unlink()
                    if self.credentials_file.exists():
                        self.credentials_file.unlink()

                logger.debug(f"Deleted credential {key}")
                return True
@@ -125,8 +128,8 @@ def delete_credential(self, key: str) -> bool:
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from JSON file."""
        try:
            if CREDENTIALS_FILE.exists():
                with open(CREDENTIALS_FILE, "r") as f:
            if self.credentials_file.exists():
                with open(self.credentials_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
@@ -167,8 +170,8 @@ def clear_all_credentials(self) -> bool:

        # Also remove credential file
        try:
            if CREDENTIALS_FILE.exists():
                CREDENTIALS_FILE.unlink()
            if self.credentials_file.exists():
                self.credentials_file.unlink()
        except Exception as e:
            logger.error(f"Error removing credential file: {e}")
            success = False