#!/usr/bin/env python3
"""
Email Sync Script

This script synchronizes emails between two IMAP mailboxes by:
1. Connecting to source and target IMAP servers
2. Searching for emails matching specified criteria in the source mailbox
3. Verifying those emails exist in the target mailbox  
4. Deleting verified emails from the source mailbox

Author: Auto-generated
Date: 2025-10-19
"""

import imaplib
import email
import json
import logging
import sys
import argparse
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
from email.header import decode_header

# Import OAuth2 helper (optional dependency)
try:
    from oauth2_helper import OAuth2Helper
    OAUTH2_AVAILABLE = True
except ImportError:
    OAUTH2_AVAILABLE = False


def check_virtual_environment():
    """Check if running in a virtual environment and provide guidance."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv and os.path.exists('venv') and not os.environ.get('SYNC_MAIL_SKIP_VENV_CHECK'):
        print("⚠️  Warning: Virtual environment detected but not activated")
        print("   Recommended: source venv/bin/activate  (Linux/macOS)")
        print("   Recommended: venv\\Scripts\\activate     (Windows)")
        print("   Or set SYNC_MAIL_SKIP_VENV_CHECK=1 to skip this check")
        print()
    
    return in_venv


def is_gmail_server(server: str) -> bool:
    """Check if the server is a Gmail server."""
    gmail_servers = [
        'imap.gmail.com',
        'imap.googlemail.com',
    ]
    return server.lower() in gmail_servers


class IMAPSync:
    """Main class for IMAP email synchronization."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the IMAP sync with configuration."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.source_conn = None
        self.target_conn = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            print("Please copy config.example.json to config.json and configure it.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sync_mail.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def connect_imap(self, mailbox_config: Dict) -> imaplib.IMAP4_SSL:
        """Connect to an IMAP server with support for both password and OAuth2 authentication."""
        try:
            server = mailbox_config['server']
            port = mailbox_config.get('port', 993)
            username = mailbox_config['username']
            
            self.logger.info(f"Connecting to {server}:{port}")
            
            # Create IMAP connection
            conn = imaplib.IMAP4_SSL(server, port)
            
            # Determine authentication method
            auth_method = mailbox_config.get('auth_method', 'password')
            
            if auth_method == 'oauth2':
                # OAuth2 authentication
                if not OAUTH2_AVAILABLE:
                    raise Exception(
                        "OAuth2 authentication requested but oauth2_helper not available. "
                        "Install dependencies: pip install google-auth google-auth-oauthlib"
                    )
                
                oauth_helper = OAuth2Helper(
                    credentials_file=mailbox_config.get('credentials_file', 'credentials.json'),
                    token_file=mailbox_config.get('token_file', 'token.json')
                )
                
                if not oauth_helper.authenticate_imap_oauth2(conn, username):
                    raise Exception("OAuth2 authentication failed")
                    
            else:
                # Traditional password authentication
                password = mailbox_config['password']
                conn.login(username, password)
            
            self.logger.info(f"Successfully connected to {server} as {username} using {auth_method}")
            return conn
            
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP connection error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to IMAP: {e}")
            raise
    
    def search_emails(self, conn: imaplib.IMAP4_SSL, folder: str, criteria: Dict, server: str = '') -> List[bytes]:
        """Search for emails matching criteria using Gmail or standard IMAP search."""
        try:
            # Check if this is a Gmail server and if Gmail search is provided
            is_gmail = is_gmail_server(server)
            
            # For Gmail with X-GM-RAW search, use [Gmail]/All Mail for comprehensive search
            # For standard IMAP or Gmail fallback, use the specified folder
            if is_gmail and 'gmail_query' in criteria:
                # Try different Gmail folder variations for All Mail
                gmail_folders = [
                    '"[Gmail]/All Mail"',    # Quoted version
                    '[Gmail]/All Mail',      # Original
                    '"All Mail"',           # Simple quoted
                    'All Mail'              # Simple
                ]
                
                selected_folder = None
                for gmail_folder in gmail_folders:
                    try:
                        status, messages = conn.select(gmail_folder)
                        if status == 'OK':
                            selected_folder = gmail_folder
                            self.logger.info(f"Using Gmail folder '{gmail_folder}' for comprehensive search")
                            break
                    except Exception:
                        continue
                
                if not selected_folder:
                    # Fallback to specified folder if All Mail variations not available
                    self.logger.info(f"Gmail All Mail folder not available, using specified folder {folder}")
                    status, messages = conn.select(folder)
                    if status != 'OK':
                        raise Exception(f"Failed to select folder {folder}")
            else:
                # Standard folder selection for non-Gmail or standard IMAP search
                status, messages = conn.select(folder)
                if status != 'OK':
                    raise Exception(f"Failed to select folder {folder}")
            
            if is_gmail and 'gmail_query' in criteria:
                # Use Gmail's native search syntax (X-GM-RAW)
                gmail_query = criteria['gmail_query']
                self.logger.info(f"Using Gmail search: {gmail_query}")
                
                try:
                    # Gmail supports X-GM-RAW for native Gmail search syntax
                    status, message_ids = conn.search(None, 'X-GM-RAW', f'"{gmail_query}"')
                    if status == 'OK':
                        message_list = message_ids[0].split() if message_ids[0] else []
                        self.logger.info(f"Found {len(message_list)} messages using Gmail search")
                        return message_list
                    else:
                        self.logger.warning(f"Gmail search failed: {status}, falling back to standard search")
                except Exception as e:
                    self.logger.warning(f"Gmail search error: {e}, falling back to standard search")
            
            # Standard IMAP search (fallback or non-Gmail servers)
            search_terms = []
            
            if 'subject' in criteria:
                search_terms.append(f'SUBJECT "{criteria["subject"]}"')
            
            if 'from' in criteria:
                search_terms.append(f'FROM "{criteria["from"]}"')
                
            if 'date_after' in criteria:
                search_terms.append(f'SINCE "{criteria["date_after"]}"')
            
            if 'to' in criteria:
                search_terms.append(f'TO "{criteria["to"]}"')
                
            if 'body' in criteria:
                search_terms.append(f'BODY "{criteria["body"]}"')
                
            if 'before_date' in criteria:
                search_terms.append(f'BEFORE "{criteria["before_date"]}"')
            
            # Default search if no criteria
            if not search_terms:
                search_terms = ['ALL']
            
            search_string = ' '.join(search_terms)
            search_type = "Gmail fallback" if is_gmail else "Standard IMAP"
            self.logger.info(f"Using {search_type} search: {search_string}")
            
            # Perform search
            status, message_ids = conn.search(None, search_string)
            if status != 'OK':
                raise Exception(f"Search failed: {status}")
            
            message_list = message_ids[0].split() if message_ids[0] else []
            self.logger.info(f"Found {len(message_list)} messages")
            
            return message_list
            
        except Exception as e:
            self.logger.error(f"Error searching emails: {e}")
            raise
    
    def get_message_info(self, conn: imaplib.IMAP4_SSL, message_id: bytes) -> Dict:
        """Get message information for verification."""
        try:
            status, message_data = conn.fetch(message_id, '(RFC822.HEADER)')
            if status != 'OK':
                raise Exception(f"Failed to fetch message {message_id}")
            
            raw_email = message_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract key information for matching
            subject = self._decode_header(email_message.get('Subject', ''))
            from_addr = self._decode_header(email_message.get('From', ''))
            message_id_header = email_message.get('Message-ID', '')
            date = email_message.get('Date', '')
            
            return {
                'subject': subject,
                'from': from_addr,
                'message_id': message_id_header,
                'date': date,
                'uid': message_id.decode()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting message info: {e}")
            raise
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header value."""
        if not header_value:
            return ''
        
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8')
                else:
                    decoded_string += part
                    
            return decoded_string
        except Exception:
            return header_value
    
    def verify_message_exists(self, conn: imaplib.IMAP4_SSL, folder: str, 
                            message_info: Dict) -> bool:
        """Verify if a message exists in the target mailbox."""
        try:
            # Select folder
            conn.select(folder)
            
            # Search by Message-ID first (most reliable)
            if message_info['message_id']:
                status, message_ids = conn.search(
                    None, f'HEADER "Message-ID" "{message_info["message_id"]}"'
                )
                if status == 'OK' and message_ids[0]:
                    return True
            
            # Fallback: search by subject and from
            search_criteria = []
            if message_info['subject']:
                search_criteria.append(f'SUBJECT "{message_info["subject"]}"')
            if message_info['from']:
                search_criteria.append(f'FROM "{message_info["from"]}"')
            
            if search_criteria:
                search_string = ' '.join(search_criteria)
                status, message_ids = conn.search(None, search_string)
                if status == 'OK' and message_ids[0]:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying message: {e}")
            return False
    
    def delete_message(self, conn: imaplib.IMAP4_SSL, message_id: bytes, 
                      dry_run: bool = False) -> bool:
        """Delete a message from the mailbox."""
        try:
            if dry_run:
                self.logger.info(f"DRY RUN: Would delete message {message_id.decode()}")
                return True
            
            # Mark message for deletion
            conn.store(message_id, '+FLAGS', '\\Deleted')
            self.logger.info(f"Marked message {message_id.decode()} for deletion")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting message {message_id.decode()}: {e}")
            return False
    
    def run_sync(self, dry_run: bool = False) -> Dict:
        """Run the email synchronization process."""
        results = {
            'processed': 0,
            'verified': 0,
            'deleted': 0,
            'errors': 0
        }
        
        try:
            # Connect to both mailboxes
            self.logger.info("Starting email synchronization")
            self.source_conn = self.connect_imap(self.config['source_mailbox'])
            self.target_conn = self.connect_imap(self.config['target_mailbox'])
            
            # Search for emails in source mailbox
            source_folder = self.config['source_mailbox']['folder']
            target_folder = self.config['target_mailbox']['folder']
            search_criteria = self.config.get('search_criteria', {})
            
            message_ids = self.search_emails(self.source_conn, source_folder, search_criteria)
            results['processed'] = len(message_ids)
            
            if not message_ids:
                self.logger.info("No messages found matching criteria")
                return results
            
            # Process each message
            for message_id in message_ids:
                try:
                    # Get message info from source
                    message_info = self.get_message_info(self.source_conn, message_id)
                    self.logger.info(f"Processing: {message_info['subject'][:50]}...")
                    
                    # Verify message exists in target
                    if self.verify_message_exists(self.target_conn, target_folder, message_info):
                        self.logger.info(f"Message verified in target mailbox")
                        results['verified'] += 1
                        
                        # Delete from source if verified
                        if self.delete_message(self.source_conn, message_id, dry_run):
                            results['deleted'] += 1
                        else:
                            results['errors'] += 1
                    else:
                        self.logger.warning(f"Message not found in target mailbox - skipping deletion")
                        
                except Exception as e:
                    self.logger.error(f"Error processing message {message_id.decode()}: {e}")
                    results['errors'] += 1
            
            # Expunge deleted messages
            if not dry_run and results['deleted'] > 0:
                self.source_conn.expunge()
                self.logger.info(f"Expunged {results['deleted']} deleted messages")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            results['errors'] += 1
            return results
            
        finally:
            # Close connections
            if self.source_conn:
                try:
                    self.source_conn.close()
                    self.source_conn.logout()
                except:
                    pass
                    
            if self.target_conn:
                try:
                    self.target_conn.close()
                    self.target_conn.logout()
                except:
                    pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sync emails between IMAP mailboxes')
    parser.add_argument('--config', default='config.json', 
                       help='Configuration file path (default: config.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform a dry run without deleting emails')
    parser.add_argument('--skip-venv-check', action='store_true',
                       help='Skip virtual environment check')
    
    args = parser.parse_args()
    
    try:
        # Check virtual environment
        if not args.skip_venv_check:
            check_virtual_environment()
        
        # Initialize and run sync
        sync = IMAPSync(args.config)
        
        # Check if dry_run is set in config
        dry_run = args.dry_run or sync.config.get('dry_run', False)
        
        if dry_run:
            print("Running in DRY RUN mode - no emails will be deleted")
        
        results = sync.run_sync(dry_run)
        
        # Print summary
        print("\n" + "="*50)
        print("SYNCHRONIZATION SUMMARY")
        print("="*50)
        print(f"Messages processed: {results['processed']}")
        print(f"Messages verified:  {results['verified']}")
        print(f"Messages deleted:   {results['deleted']}")
        print(f"Errors:            {results['errors']}")
        
        if dry_run:
            print("\nNOTE: This was a dry run - no emails were actually deleted")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()