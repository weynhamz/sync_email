# Email Sync Project

A Python script for synchronizing emails between two IMAP mailboxes. This tool can confirm that a mail message is available on one mailbox and then delete it from another.

## Features

- Connect to two IMAP mailboxes
- Search for specific emails
- Verify email existence before deletion
- Secure credential management
- Comprehensive logging
- JSON-based configuration

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy and configure the settings:
   ```bash
   cp config.example.json config.json
   ```

3. Edit `config.json` with your IMAP server details and credentials.

## Configuration

Edit `config.json` with your IMAP server settings:

```json
{
  "source_mailbox": {
    "server": "imap.example.com",
    "port": 993,
    "username": "source@example.com",
    "password": "your_password",
    "folder": "INBOX"
  },
  "target_mailbox": {
    "server": "imap.target.com", 
    "port": 993,
    "username": "target@example.com",
    "password": "your_password",
    "folder": "INBOX"
  },
  "search_criteria": {
    "subject": "Test Email",
    "from": "sender@example.com",
    "date_after": "01-Jan-2024"
  },
  "log_level": "INFO"
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