# Email Sync Project

A Python script for synchronizing emails between two IMAP mailboxes. This tool can confirm that a mail message is available on one mailbox and then delete it from another.

## Features

- Connect to two IMAP mailboxes
- **Gmail OAuth2 support** - No need for app passwords!
- Traditional password authentication for other providers
- Search for specific emails
- Verify email existence before deletion
- Secure credential management
- Comprehensive logging
- JSON-based configuration

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Quick Start

### Basic Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy and configure the settings:
   ```bash
   cp config.example.json config.json
   ```

3. Edit `config.json` with your IMAP server details.

### Gmail OAuth2 Setup

For Gmail accounts, OAuth2 is recommended over app passwords:

1. **Use OAuth2 example config**:
   ```bash
   cp config.oauth2.example.json config.json
   ```

2. **Follow the OAuth2 setup guide**: See [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for detailed instructions

3. **Quick OAuth2 test**:
   ```bash
   python oauth2_helper.py --setup  # Show setup instructions
   python oauth2_helper.py --test   # Test configuration
   ```

## Configuration

### Password Authentication (Traditional)

Edit `config.json` with your IMAP server settings:

```json
{
  "source_mailbox": {
    "server": "imap.example.com",
    "port": 993,
    "username": "source@example.com",
    "auth_method": "password",
    "password": "your_password",
    "folder": "INBOX"
  },
  "target_mailbox": {
    "server": "imap.target.com", 
    "port": 993,
    "username": "target@example.com",
    "auth_method": "password",
    "password": "your_password",
    "folder": "INBOX"
  }
}
```

### OAuth2 Authentication (Gmail)

For Gmail accounts, use OAuth2 (recommended):

```json
{
  "source_mailbox": {
    "server": "imap.gmail.com",
    "port": 993,
    "username": "your-email@gmail.com",
    "auth_method": "oauth2",
    "credentials_file": "credentials.json",
    "token_file": "token.json",
    "folder": "INBOX"
  }
}
```

**Note**: See [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for complete OAuth2 setup instructions.

### Mixed Authentication

You can mix authentication methods:

```json
{
  "source_mailbox": {
    "auth_method": "oauth2",
    "server": "imap.gmail.com",
    "username": "gmail@gmail.com"
  },
  "target_mailbox": {
    "auth_method": "password", 
    "server": "imap.outlook.com",
    "username": "outlook@outlook.com",
    "password": "app_password"
  }
}
```

## Usage

Run the email sync script:

```bash
python sync_mail.py
```

The script will:
1. Connect to both IMAP mailboxes
2. Search for emails matching the criteria in the source mailbox
3. Verify the emails exist in the target mailbox
4. Delete the verified emails from the source mailbox

## Safety Features

- Dry-run mode (use `--dry-run` flag)
- Confirmation prompts before deletion
- Detailed logging of all operations
- Backup recommendations

## Logging

Logs are written to `sync_mail.log` with timestamps and operation details.

## Security Notes

- Store credentials securely
- Use app-specific passwords when available
- Consider using environment variables for sensitive data
- Test with non-critical emails first

## License

MIT License