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
            # Convert bytes to string for IMAP fetch command
            if isinstance(message_id, bytes):
                msg_id_str = message_id.decode('utf-8')
            else:
                msg_id_str = str(message_id)
            
            status, message_data = conn.fetch(msg_id_str, '(RFC822.HEADER)')
            if status != 'OK':
                raise Exception(f"Failed to fetch message {message_id}")
            
            if not message_data or not message_data[0] or len(message_data[0]) < 2:
                raise Exception(f"Invalid message data for {message_id}")
                
            raw_email = message_data[0][1]
            if not raw_email or not isinstance(raw_email, bytes):
                raise Exception(f"Invalid message content for {message_id}")
                
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
                'uid': message_id.decode() if isinstance(message_id, bytes) else str(message_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting message info: {e}")
            raise
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header value with improved Unicode handling."""
        if not header_value:
            return ''
        
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    # Try specific encoding first, then fallback to utf-8, then latin-1
                    try:
                        decoded_string += part.decode(encoding or 'utf-8')
                    except (UnicodeDecodeError, LookupError):
                        try:
                            decoded_string += part.decode('utf-8')
                        except UnicodeDecodeError:
                            decoded_string += part.decode('latin-1', errors='replace')
                else:
                    decoded_string += str(part)
                    
            return decoded_string
        except Exception as e:
            # Return sanitized version if all else fails
            try:
                return str(header_value).encode('ascii', errors='replace').decode('ascii')
            except Exception:
                return f"[Encoding Error: {str(e)}]"
    
    def _safe_log_string(self, text: str) -> str:
        """Create a safe ASCII representation of text for logging."""
        if not text:
            return ''
        try:
            # Try to encode as ASCII, replacing non-ASCII characters
            return text.encode('ascii', errors='replace').decode('ascii')
        except Exception:
            return '[Encoding Error]'
    
    def _safe_search_string(self, text: str) -> str:
        """Create a safe ASCII string for IMAP search commands."""
        if not text:
            return ''
        try:
            # Extract ASCII-only parts, skip non-ASCII to avoid IMAP errors
            ascii_text = ''.join(char for char in text if ord(char) < 128 and char.isprintable())
            # Remove extra spaces and quotes that could break IMAP search
            cleaned = ' '.join(ascii_text.replace('"', '').split())
            # Only return if we have meaningful text
            if len(cleaned) >= 3:
                # For email addresses, preserve them as-is
                if '@' in cleaned and '.' in cleaned:
                    return cleaned
                # For other text, only return if it has some letters
                elif any(c.isalpha() for c in cleaned):
                    return cleaned
            return ''
        except Exception:
            return ''
    
    def _apply_to_delete_marker(self, conn: imaplib.IMAP4_SSL, msg_id_str: str, server: str) -> bool:
        """Apply _TO_DELETE label for Gmail or move to _TO_DELETE folder for other servers."""
        try:
            if is_gmail_server(server):
                # For Gmail, add the _TO_DELETE label
                try:
                    # Add the label using Gmail's X-GM-LABELS extension
                    status, response = conn.store(msg_id_str, '+X-GM-LABELS', '("_TO_DELETE")')
                    if status == 'OK':
                        self.logger.debug(f"Added _TO_DELETE label to Gmail message {msg_id_str}")
                        return True
                    else:
                        # Fallback: try standard IMAP flags if X-GM-LABELS doesn't work
                        status, response = conn.store(msg_id_str, '+FLAGS', '(_TO_DELETE)')
                        return status == 'OK'
                except Exception as e:
                    self.logger.debug(f"Gmail label failed, trying standard flag: {e}")
                    # Fallback to standard IMAP flag
                    status, response = conn.store(msg_id_str, '+FLAGS', '(_TO_DELETE)')
                    return status == 'OK'
            else:
                # For other IMAP servers, try to move to _TO_DELETE folder
                try:
                    # First, ensure the _TO_DELETE folder exists
                    try:
                        conn.create('_TO_DELETE')
                    except Exception:
                        pass  # Folder might already exist
                    
                    # Move the message to _TO_DELETE folder
                    status, response = conn.move(msg_id_str, '_TO_DELETE')
                    if status == 'OK':
                        self.logger.debug(f"Moved message {msg_id_str} to _TO_DELETE folder")
                        return True
                    else:
                        # Fallback: copy and mark for deletion if move doesn't work
                        status, response = conn.copy(msg_id_str, '_TO_DELETE')
                        if status == 'OK':
                            self.logger.debug(f"Copied message {msg_id_str} to _TO_DELETE folder")
                            return True
                        return False
                except Exception as e:
                    self.logger.debug(f"Failed to move/copy message to _TO_DELETE folder: {e}")
                    # Final fallback: just add a flag
                    status, response = conn.store(msg_id_str, '+FLAGS', '(_TO_DELETE)')
                    return status == 'OK'
        except Exception as e:
            self.logger.error(f"Error applying _TO_DELETE marker: {e}")
            return False
    
    def verify_message_exists(self, conn: imaplib.IMAP4_SSL, folder: str, 
                            message_info: Dict, server: str = '') -> bool:
        """Verify if a message exists in the target mailbox."""
        try:
            # Use Gmail folder optimization for target mailbox too
            is_gmail = is_gmail_server(server)
            
            if is_gmail:
                # For Gmail, try to use All Mail folder for comprehensive search
                gmail_folders = [
                    '"[Gmail]/All Mail"',    # Quoted version
                    '[Gmail]/All Mail',      # Original
                    folder                   # Fallback to specified folder
                ]
                
                selected_folder = None
                for gmail_folder in gmail_folders:
                    try:
                        status, messages = conn.select(gmail_folder)
                        if status == 'OK':
                            selected_folder = gmail_folder
                            self.logger.debug(f"Using Gmail folder '{gmail_folder}' for verification")
                            break
                    except Exception:
                        continue
                
                if not selected_folder:
                    self.logger.warning(f"Could not select any Gmail folder for verification")
                    return False
            else:
                # Standard folder selection for non-Gmail
                status, messages = conn.select(folder)
                if status != 'OK':
                    self.logger.warning(f"Could not select folder {folder} for verification")
                    return False
            
            # Search by Message-ID first (most reliable)
            if message_info['message_id']:
                try:
                    # Clean Message-ID for search (remove angle brackets if present)
                    clean_msg_id = message_info['message_id'].strip('<>')
                    self.logger.debug(f"Searching for Message-ID: {clean_msg_id}")
                    status, message_ids = conn.search(
                        None, f'HEADER "Message-ID" "{clean_msg_id}"'
                    )
                    if status == 'OK' and message_ids[0]:
                        self.logger.debug(f"Found message by Message-ID: {message_ids[0]}")
                        return True
                    else:
                        self.logger.debug(f"Message-ID search returned: status={status}, ids={message_ids}")
                except Exception as e:
                    self.logger.debug(f"Message-ID search failed: {e}")
                    # Continue to fallback search
            
            # Fallback: search by subject and from (sanitize non-ASCII characters)
            # Try individual searches to avoid complex search string parsing issues
            if message_info['subject']:
                try:
                    safe_subject = self._safe_search_string(message_info['subject'])
                    if safe_subject and len(safe_subject) >= 5:  # Meaningful subject search
                        status, message_ids = conn.search(None, f'SUBJECT "{safe_subject}"')
                        if status == 'OK' and message_ids[0]:
                            return True
                except Exception as e:
                    self.logger.debug(f"Subject search failed: {e}")
            
            if message_info['from']:
                try:
                    safe_from = self._safe_search_string(message_info['from'])
                    if safe_from and '@' in safe_from:  # Meaningful email search
                        status, message_ids = conn.search(None, f'FROM "{safe_from}"')
                        if status == 'OK' and message_ids[0]:
                            return True
                except Exception as e:
                    self.logger.debug(f"From search failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying message: {e}")
            return False
    
    def delete_message(self, conn: imaplib.IMAP4_SSL, message_id: bytes, 
                      dry_run: bool = False, message_subject: str = '', 
                      current_index: int = 0, total_count: int = 0, deletion_count: int = 0, 
                      server: str = '') -> bool:
        """Delete a message from the mailbox."""
        try:
            # Convert message_id to string for consistency
            msg_id_str = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
            
            if dry_run:
                # Instead of just logging, apply _TO_DELETE label/folder for dry run
                success = self._apply_to_delete_marker(conn, msg_id_str, server)
                if success:
                    if message_subject and deletion_count > 0 and total_count > 0:
                        self.logger.info(f"({deletion_count} of {total_count}) DRY RUN: Would delete message - ID: {msg_id_str} - Subject: {message_subject}")
                    else:
                        self.logger.info(f"DRY RUN: Would delete message - ID: {msg_id_str}")
                else:
                    if message_subject and deletion_count > 0 and total_count > 0:
                        self.logger.warning(f"({deletion_count} of {total_count}) DRY RUN: Would delete message - ID: {msg_id_str} - Subject: {message_subject}")
                    else:
                        self.logger.warning(f"DRY RUN: Failed to apply _TO_DELETE marker to message {msg_id_str}")
                return success
            
            # Mark message for deletion (convert back to string for store command)
            conn.store(msg_id_str, '+FLAGS', '\\Deleted')
            if deletion_count > 0 and total_count > 0:
                self.logger.info(f"({deletion_count} of {total_count}) Marked message (ID: {msg_id_str}) for deletion")
            elif deletion_count > 0:
                self.logger.info(f"Marked message #{deletion_count} (ID: {msg_id_str}) for deletion")
            else:
                self.logger.info(f"Marked message {msg_id_str} for deletion")
            return True
            
        except Exception as e:
            msg_id_str = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
            self.logger.error(f"Error deleting message {msg_id_str}: {e}")
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
            source_server = self.config['source_mailbox']['server']
            target_server = self.config['target_mailbox']['server']
            
            message_ids = self.search_emails(self.source_conn, source_folder, search_criteria, source_server)
            results['processed'] = len(message_ids)
            
            if not message_ids:
                self.logger.info("No messages found matching criteria")
                return results
            
            # Process each message
            total_count = len(message_ids)
            deletion_count = 0  # Separate counter for messages to be deleted
            for current_index, message_id in enumerate(message_ids, 1):
                try:
                    # Get message info from source
                    message_info = self.get_message_info(self.source_conn, message_id)
                    # Display Unicode characters properly in logging
                    display_subject = message_info['subject'][:50] if message_info['subject'] else '[No Subject]'
                    self.logger.info(f"[{current_index}/{total_count}] Processing: {display_subject}...")
                    
                    # Verify message exists in target
                    self.logger.debug(f"Verifying message in target: Message-ID={message_info.get('message_id', 'None')}, Subject={message_info.get('subject', 'None')[:30]}")
                    if self.verify_message_exists(self.target_conn, target_folder, message_info, target_server):
                        self.logger.info(f"Message verified in target mailbox")
                        results['verified'] += 1
                        
                        # Increment deletion counter
                        deletion_count += 1
                        
                        # Delete from source if verified
                        if self.delete_message(self.source_conn, message_id, dry_run, display_subject, current_index, total_count, deletion_count, source_server):
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
