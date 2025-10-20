# Gmail OAuth2 Setup Guide

This guide explains how to set up Gmail OAuth2 authentication for the email sync tool.

## Prerequisites

1. **Install OAuth2 dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2
   ```

2. **Google Cloud Project**: You need a Google Cloud project with Gmail API enabled.

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project name/ID

### 2. Enable Gmail API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

### 3. Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in required fields (app name, user support email)
   - Add your email to test users
4. For application type, choose **Desktop application**
5. Give it a name (e.g., "Email Sync Tool")
6. Click **Create**

### 4. Download Credentials

1. After creating the OAuth client, click the download button (⬇️)
2. Save the file as `credentials.json` in your project directory
3. **Important**: Keep this file secure and don't commit it to version control

### 5. Configure Email Sync

1. Update your `config.json` to use OAuth2:
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

2. Or use the OAuth2 example config:
   ```bash
   cp config.oauth2.example.json config.json
   # Edit config.json with your email address
   ```

### 6. First Run Authorization

1. Run the sync tool:
   ```bash
   python sync_mail.py --dry-run
   ```

2. A browser window will open automatically
3. Sign in to your Google account
4. Grant permissions to the application
5. The browser will show "The authentication flow has completed"
6. A `token.json` file will be created automatically

### 7. Verify Setup

Test your OAuth2 setup:
```bash
python oauth2_helper.py --test
```

## Configuration Options

### OAuth2 Mailbox Configuration

```json
{
  "server": "imap.gmail.com",
  "port": 993,
  "username": "your-email@gmail.com",
  "auth_method": "oauth2",
  "credentials_file": "credentials.json",  // Optional, default: credentials.json
  "token_file": "token.json",              // Optional, default: token.json
  "folder": "INBOX"
}
```

### Mixed Authentication

You can use OAuth2 for Gmail and password authentication for other providers:

```json
{
  "source_mailbox": {
    "server": "imap.gmail.com",
    "username": "gmail-user@gmail.com",
    "auth_method": "oauth2"
  },
  "target_mailbox": {
    "server": "imap.outlook.com", 
    "username": "outlook-user@outlook.com",
    "auth_method": "password",
    "password": "app-password"
  }
}
```

## Security Notes

1. **Credentials File**: Never commit `credentials.json` to version control
2. **Token File**: The `token.json` contains access tokens - keep it secure
3. **Scopes**: The tool requests minimal required permissions:
   - `gmail.readonly`: Read email messages
   - `gmail.modify`: Delete email messages
4. **Token Refresh**: Access tokens are automatically refreshed when needed

## Troubleshooting

### Common Issues

1. **"OAuth2 authentication failed"**
   - Check that Gmail API is enabled in Google Cloud Console
   - Verify `credentials.json` is valid and in the correct location
   - Try deleting `token.json` and re-authorizing

2. **"Invalid credentials"**
   - Make sure you're using the correct Google account
   - Check that the OAuth consent screen is configured
   - Verify your email is added as a test user

3. **"Access blocked"**
   - Your app might need verification for production use
   - For testing, add your email to test users in OAuth consent screen

4. **Browser doesn't open**
   - The tool uses a local server on a random port
   - Check firewall settings
   - You can manually copy the URL from the console

### OAuth2 Setup Helper

Use the built-in helper for setup assistance:

```bash
# Show setup instructions
python oauth2_helper.py --setup

# Test OAuth2 configuration
python oauth2_helper.py --test

# Use custom files
python oauth2_helper.py --credentials my-creds.json --token my-token.json --test
```

## File Structure

After setup, your project should have:

```
sync_mail/
├── credentials.json          # OAuth2 credentials (keep secure!)
├── token.json               # Access tokens (auto-generated)
├── config.json              # Your configuration
├── config.oauth2.example.json  # OAuth2 example config
├── oauth2_helper.py         # OAuth2 implementation
└── sync_mail.py            # Main sync script
```

## Next Steps

Once OAuth2 is configured:

1. Test with dry-run: `python sync_mail.py --dry-run`
2. Run actual sync: `python sync_mail.py`
3. Monitor logs for any authentication issues
4. Tokens will be automatically refreshed as needed