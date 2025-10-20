#!/usr/bin/env python3
"""
OAuth2 authentication helper for Gmail IMAP access.

This module provides OAuth2 authentication for Gmail using Google's OAuth2 flow.
It handles token acquisition, refresh, and XOAUTH2 SASL authentication.

Author: Auto-generated
Date: 2025-10-19
"""

import json
import base64
import os
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    import google.auth.exceptions
    OAUTH2_AVAILABLE = True
except ImportError:
    # Create placeholder classes for type hints when imports fail
    class Credentials:
        pass
    class Request:
        pass
    class InstalledAppFlow:
        pass
    OAUTH2_AVAILABLE = False


class OAuth2Helper:
    """Helper class for Gmail OAuth2 authentication."""
    
    # Gmail IMAP scope
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
              'https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials_file: str = "credentials.json", 
                 token_file: str = "token.json"):
        """
        Initialize OAuth2 helper.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load access tokens
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.logger = logging.getLogger(__name__)
        
        if not OAUTH2_AVAILABLE:
            self.logger.warning(
                "OAuth2 dependencies not available. "
                "Install with: pip install google-auth google-auth-oauthlib"
            )
        
    def get_oauth2_credentials(self) -> Optional[Credentials]:
        """
        Get OAuth2 credentials, handling token refresh if needed.
        
        Returns:
            Valid OAuth2 credentials or None if failed
        """
        if not OAUTH2_AVAILABLE:
            self.logger.error("OAuth2 dependencies not available")
            return None
            
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
                self.logger.info("Loaded existing OAuth2 token")
            except Exception as e:
                self.logger.warning(f"Error loading token file: {e}")
        
        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self.logger.info("Refreshed OAuth2 token")
                self._save_credentials(creds)
            except google.auth.exceptions.RefreshError as e:
                self.logger.error(f"Failed to refresh token: {e}")
                creds = None
        
        # Run OAuth2 flow if no valid credentials
        if not creds or not creds.valid:
            creds = self._run_oauth_flow()
        
        return creds
    
    def _run_oauth_flow(self) -> Optional[Credentials]:
        """
        Run the OAuth2 authorization flow.
        
        Returns:
            Valid OAuth2 credentials or None if failed
        """
        if not os.path.exists(self.credentials_file):
            self.logger.error(f"Credentials file not found: {self.credentials_file}")
            self.logger.error("Please download credentials.json from Google Cloud Console")
            return None
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES
            )
            
            # Run local server flow
            self.logger.info("Starting OAuth2 authorization flow...")
            creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            self._save_credentials(creds)
            self.logger.info("OAuth2 authorization completed successfully")
            
            return creds
            
        except Exception as e:
            self.logger.error(f"OAuth2 flow failed: {e}")
            return None
    
    def _save_credentials(self, creds: Credentials) -> None:
        """Save credentials to token file."""
        try:
            with open(self.token_file, 'w') as f:
                f.write(creds.to_json())
            self.logger.debug(f"Saved credentials to {self.token_file}")
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def generate_xoauth2_string(self, email: str, access_token: str) -> str:
        """
        Generate XOAUTH2 authentication string.
        
        Args:
            email: User's email address
            access_token: OAuth2 access token
            
        Returns:
            Base64-encoded XOAUTH2 string
        """
        auth_string = f'user={email}\x01auth=Bearer {access_token}\x01\x01'
        return base64.b64encode(auth_string.encode()).decode()
    
    def authenticate_imap_oauth2(self, conn, email: str) -> bool:
        """
        Authenticate IMAP connection using OAuth2.
        
        Args:
            conn: IMAP connection object
            email: User's email address
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Get OAuth2 credentials
            creds = self.get_oauth2_credentials()
            if not creds or not creds.token:
                self.logger.error("Failed to get valid OAuth2 credentials")
                return False
            
            # Generate XOAUTH2 string
            auth_string = self.generate_xoauth2_string(email, creds.token)
            
            # Authenticate using XOAUTH2
            response = conn.authenticate('XOAUTH2', lambda x: auth_string)
            
            if response[0] == 'OK':
                self.logger.info(f"OAuth2 authentication successful for {email}")
                return True
            else:
                self.logger.error(f"OAuth2 authentication failed: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"OAuth2 authentication error: {e}")
            return False
    
    def is_oauth2_configured(self) -> bool:
        """
        Check if OAuth2 is properly configured.
        
        Returns:
            True if credentials file exists and OAuth2 libraries are available
        """
        return OAUTH2_AVAILABLE and os.path.exists(self.credentials_file)
    
    def setup_oauth2_credentials(self) -> Dict[str, str]:
        """
        Provide instructions for setting up OAuth2 credentials.
        
        Returns:
            Dictionary with setup instructions
        """
        return {
            "step1": "Go to Google Cloud Console (console.cloud.google.com)",
            "step2": "Create a new project or select existing project",
            "step3": "Enable Gmail API for your project",
            "step4": "Go to Credentials → Create Credentials → OAuth 2.0 Client IDs",
            "step5": "Choose 'Desktop application' as application type",
            "step6": "Download the credentials JSON file",
            "step7": f"Save the file as '{self.credentials_file}' in your project directory",
            "step8": "Run the sync script - it will open a browser for authorization",
            "note": "You only need to authorize once. Tokens will be automatically refreshed."
        }


def setup_oauth2_cli():
    """Command-line interface for OAuth2 setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OAuth2 Setup Helper for Gmail')
    parser.add_argument('--credentials', default='credentials.json',
                       help='Path to credentials JSON file')
    parser.add_argument('--token', default='token.json',
                       help='Path to token file')
    parser.add_argument('--test', action='store_true',
                       help='Test OAuth2 authentication')
    parser.add_argument('--setup', action='store_true',
                       help='Show setup instructions')
    
    args = parser.parse_args()
    
    oauth_helper = OAuth2Helper(args.credentials, args.token)
    
    if args.setup:
        print("OAuth2 Setup Instructions:")
        print("=" * 40)
        instructions = oauth_helper.setup_oauth2_credentials()
        for key, value in instructions.items():
            print(f"{key}: {value}")
        return
    
    if args.test:
        print("Testing OAuth2 configuration...")
        if oauth_helper.is_oauth2_configured():
            print("✓ OAuth2 libraries available")
            print("✓ Credentials file found")
            
            creds = oauth_helper.get_oauth2_credentials()
            if creds and creds.valid:
                print("✓ OAuth2 authentication successful")
                print(f"✓ Token expires: {creds.expiry}")
            else:
                print("✗ OAuth2 authentication failed")
        else:
            print("✗ OAuth2 not properly configured")
            if not OAUTH2_AVAILABLE:
                print("  Missing dependencies: pip install google-auth google-auth-oauthlib")
            if not os.path.exists(args.credentials):
                print(f"  Missing credentials file: {args.credentials}")


if __name__ == "__main__":
    setup_oauth2_cli()