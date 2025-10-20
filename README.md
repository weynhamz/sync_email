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

### 🚀 Automated Setup (Recommended)

**One-command setup with virtual environment:**

```bash
./setup.sh
```

This script will:
- Create and activate a Python virtual environment
- Install all dependencies
- Set up configuration files
- Validate the installation

### 📋 Manual Setup

#### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Optional: Install development tools
pip install -r requirements-dev.txt
```

#### 3. Configure the Application

```bash
# For password authentication:
cp config.example.json config.json

# For Gmail OAuth2:
cp config.oauth2.example.json config.json

# Edit config.json with your settings
```

### 💡 Quick Test

```bash
# Test configuration
python config_helper.py validate

# Test sync (dry run - no emails deleted)
python sync_mail.py --dry-run
```

### Gmail OAuth2 Setup

For Gmail accounts, OAuth2 is recommended over app passwords:

1. **Use OAuth2 example config**:
   ```bash
   cp config.oauth2.example.json config.json
   ```

2. **Follow the OAuth2 setup guide**: See [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for detailed instructions

3. **Gmail search guide**: See [GMAIL_SEARCH.md](GMAIL_SEARCH.md) for powerful Gmail search syntax

4. **Quick OAuth2 test**:
   ```bash
   python oauth2_helper.py --setup  # Show setup instructions
   python oauth2_helper.py --test   # Test configuration
   ```

## Virtual Environment Management

### 🔄 Daily Usage

**Activate virtual environment** (do this each time you use the tool):

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Deactivate when done:**
```bash
deactivate
```

### 📦 Dependency Management

**Add new dependencies:**
```bash
pip install package-name
pip freeze > requirements.txt  # Update requirements
```

**Update existing dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**Development environment:**
```bash
pip install -r requirements-dev.txt  # Install linting, testing tools
```

### 🛠️ Development Tools

With development dependencies installed:

```bash
# Format code
black *.py

# Sort imports
isort *.py

# Run linting
flake8 *.py

# Run type checking
mypy sync_mail.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html
```

### 🔍 Environment Check

**Check your setup** at any time:

```bash
python env_check.py
```

This comprehensive check will verify:
- ✅ Python version compatibility
- 📦 Virtual environment status  
- 📚 Required and optional dependencies
- ⚙️ Configuration file validity
- 🔐 OAuth2 setup status
- 📄 Project file integrity

**Quick environment info:**
```bash
python sync_mail.py --help  # Also shows venv warning if needed
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

### 🔍 Search Criteria Configuration

The email sync tool supports flexible search criteria with **enhanced Gmail search support**.

#### **Gmail Search (Recommended for Gmail)**

For Gmail servers, you can use Gmail's powerful native search syntax:

```json
{
  "search_criteria": {
    "gmail_query": "from:sender@example.com subject:\"Important Email\" after:2024/1/1 -label:spam"
  }
}
```

**Gmail Search Examples:**
```json
// Find emails from specific sender with attachments
"gmail_query": "from:boss@company.com has:attachment"

// Find emails in date range with specific subject
"gmail_query": "subject:\"Project Update\" after:2024/1/1 before:2024/12/31"

// Find emails excluding certain labels
"gmail_query": "from:notifications@github.com -label:important -is:unread"

// Find emails with specific labels and categories  
"gmail_query": "label:work category:updates after:2024/6/1"

// Complex query with multiple criteria
"gmail_query": "from:client@company.com OR to:team@mycompany.com has:attachment -label:archived"
```

**Gmail Search Operators:**
- `from:`, `to:`, `cc:`, `bcc:` - Email addresses
- `subject:` - Subject line text
- `after:`, `before:` - Date ranges (YYYY/MM/DD)
- `has:attachment` - Emails with attachments
- `label:`, `-label:` - Include/exclude labels
- `is:unread`, `is:read` - Read status
- `category:` - Gmail categories (updates, social, etc.)
- `OR`, `AND` - Boolean operators
- Parentheses for grouping: `(from:a@b.com OR from:c@d.com)`

#### **Standard IMAP Search (All Providers)**

For non-Gmail servers or as fallback, use standard IMAP criteria:

```json
{
  "search_criteria": {
    "subject": "Test Email",
    "from": "sender@example.com", 
    "to": "recipient@example.com",
    "body": "keyword in body",
    "date_after": "01-Jan-2024",
    "before_date": "31-Dec-2024"
  }
}
```

#### **Mixed Configuration**

You can specify both Gmail and standard criteria. Gmail search takes precedence for Gmail servers:

```json
{
  "search_criteria": {
    "gmail_query": "from:sender@example.com after:2024/1/1",
    "subject": "Test Email",
    "from": "sender@example.com",
    "date_after": "01-Jan-2024"
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

## Development Setup Summary

### 🎯 One-Command Setup
```bash
./setup.sh  # Creates venv, installs dependencies, sets up config
```

### 📁 Project Structure
```
sync_mail/
├── setup.sh                      # Automated setup script
├── env_check.py                   # Environment validation
├── requirements.txt               # Main dependencies  
├── requirements-dev.txt           # Development tools
├── sync_mail.code-workspace       # VS Code workspace
├── .vscode/settings.json          # VS Code Python settings
├── venv/                          # Virtual environment (created by setup)
├── sync_mail.py                   # Main application
├── oauth2_helper.py               # OAuth2 authentication
├── config_helper.py               # Configuration utilities
├── OAUTH2_SETUP.md               # OAuth2 setup guide
├── GMAIL_SEARCH.md               # Gmail search syntax guide
├── gmail_search_demo.py           # Gmail search demonstration
└── test_gmail_search.py           # Gmail search tests
```

### 🔧 VS Code Integration
- **Automatic Python interpreter** detection (`./venv/bin/python`)
- **Built-in tasks**: Setup, Test, Format, Run Sync
- **Code quality** tools: Black, isort, Flake8, Pylint, MyPy
- **Testing integration** with pytest
- **Recommended extensions** for Python development

### ⚡ Quick Commands
```bash
# Setup and activate environment
./setup.sh && source venv/bin/activate

# Validate everything
python env_check.py

# Test configuration
python config_helper.py validate

# Run sync (safe mode)
python sync_mail.py --dry-run
```

## License

MIT License