# Security & Privacy

This document outlines the security measures implemented in the ROM Cleanup Tool to protect your data and API credentials.

## Credential Security

### Secure Storage
The ROM Cleanup Tool now uses secure credential storage to protect your API keys:

1. **Primary Method: Keyring**
   - Uses your system's secure credential storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
   - Credentials are encrypted by the operating system
   - No plaintext storage on disk

2. **Fallback Method: Encrypted Local Storage**
   - If keyring is unavailable, credentials are stored locally with AES encryption
   - Encryption keys are stored separately with restrictive file permissions
   - Files are only readable by your user account

3. **No Hardcoded Secrets**
   - No API keys or tokens are embedded in the code
   - All credentials must be provided by the user
   - Source code can be safely shared and version controlled

### Installation for Enhanced Security

For the most secure credential storage, install the security dependencies:

```bash
# Install with security features
pip install -e ".[security]"

# Or install security dependencies manually
pip install keyring cryptography
```

Without these dependencies, the tool will still function but will warn about reduced security.

### API Key Best Practices

#### TheGamesDB API Key
- Keep your API key private and never share it
- The key is provided via Discord - join their community respectfully
- Regenerate your key if you suspect it's been compromised

#### IGDB Credentials
- Client ID and Access Token are provided via Twitch Developer Console
- Access tokens expire - the tool will warn you when renewal is needed
- Never commit these credentials to version control

### Data Privacy

#### Local Processing
- All ROM file analysis happens locally on your machine
- No ROM file data is sent to external services
- Only game names are sent to APIs for matching (when enabled)

#### API Communication
- Communication with TheGamesDB/IGDB uses HTTPS encryption
- API requests include minimal data (game names only)
- No personal information is transmitted

#### Cache Security
- Game name caches are stored locally in plaintext
- Caches contain only game metadata (names, IDs)
- No sensitive information is cached

### File Operation Safety

#### Dry Run Mode
- Always test with `--dry-run` first
- Shows exactly what would be modified
- No files are moved or deleted in dry run mode

#### Safe Move Operation
- Default operation moves files to `to_delete` folder
- Allows manual review before permanent deletion
- Original directory structure is preserved

#### Backup Recommendations
- Always backup your ROM collection before running the tool
- Test on a small subset first
- Verify results before processing large collections

### Permissions and Access

#### File System Access
- Tool only accesses the directories you specify
- No automatic scanning of system directories
- Respects file system permissions

#### Network Access
- Only connects to configured APIs (TheGamesDB/IGDB)
- No telemetry or usage tracking
- No automatic updates or external connections

### Vulnerability Reporting

If you discover a security vulnerability in this tool:

1. **Do NOT** create a public issue
2. Contact the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

### Security Checklist

Before using the ROM Cleanup Tool:

- [ ] Install security dependencies (`pip install keyring cryptography`)
- [ ] Verify your API credentials are stored securely
- [ ] Test with `--dry-run` on a small directory first
- [ ] Backup your ROM collection
- [ ] Review the files marked for removal
- [ ] Ensure you understand what the tool will do

### Threat Model

The ROM Cleanup Tool is designed to protect against:

- **Credential theft**: API keys stored securely, not in plaintext
- **Accidental data loss**: Dry run mode and safe move operations
- **Unauthorized access**: No network services, local operation only
- **Information disclosure**: Minimal data sent to APIs

The tool does NOT protect against:
- Physical access to your computer (use disk encryption)
- Malware on your system (use antivirus software)
- Social engineering attacks (keep credentials private)
- Network eavesdropping on unencrypted connections (APIs use HTTPS)

### Regular Security Maintenance

Recommended security practices:

1. **Rotate API Keys**: Regenerate API keys periodically
2. **Update Dependencies**: Keep the tool and its dependencies updated
3. **Monitor Usage**: Review API usage in your developer consoles
4. **Clear Caches**: Periodically clear game name caches if privacy is a concern
5. **Check Permissions**: Ensure cache and credential files have appropriate permissions

For more information about specific security features, see the documentation for the `credential_manager` module.