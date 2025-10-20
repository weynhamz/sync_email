#!/usr/bin/env python3
"""
Test Gmail search functionality without requiring actual Gmail connection.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from sync_mail import IMAPSync, is_gmail_server


class TestGmailSearch(unittest.TestCase):
    """Test Gmail search functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Gmail configuration with Gmail search
        self.gmail_config = {
            "source_mailbox": {
                "server": "imap.gmail.com",
                "port": 993,
                "username": "test@gmail.com",
                "auth_method": "oauth2",
                "folder": "INBOX"
            },
            "target_mailbox": {
                "server": "imap.outlook.com",
                "port": 993,
                "username": "test@outlook.com",
                "auth_method": "password",
                "password": "testpass",
                "folder": "INBOX"
            },
            "search_criteria": {
                "gmail_query": "from:sender@example.com after:2024/1/1",
                "subject": "Test Email",
                "from": "sender@example.com"
            },
            "log_level": "INFO"
        }
        
        # Non-Gmail configuration 
        self.standard_config = {
            "source_mailbox": {
                "server": "imap.outlook.com",
                "port": 993,
                "username": "test@outlook.com",
                "auth_method": "password",
                "password": "testpass",
                "folder": "INBOX"
            },
            "target_mailbox": {
                "server": "imap.example.com",
                "port": 993,
                "username": "test@example.com",
                "auth_method": "password",
                "password": "testpass",
                "folder": "INBOX"
            },
            "search_criteria": {
                "subject": "Test Email",
                "from": "sender@example.com",
                "date_after": "01-Jan-2024"
            },
            "log_level": "INFO"
        }
    
    def test_gmail_server_detection(self):
        """Test Gmail server detection function."""
        # Test Gmail servers
        self.assertTrue(is_gmail_server("imap.gmail.com"))
        self.assertTrue(is_gmail_server("imap.googlemail.com"))
        self.assertTrue(is_gmail_server("IMAP.GMAIL.COM"))  # Case insensitive
        
        # Test non-Gmail servers
        self.assertFalse(is_gmail_server("imap.outlook.com"))
        self.assertFalse(is_gmail_server("imap.yahoo.com"))
        self.assertFalse(is_gmail_server("mail.example.com"))
    
    @patch('sync_mail.imaplib.IMAP4_SSL')
    def test_gmail_search_functionality(self, mock_imap):
        """Test Gmail X-GM-RAW search functionality."""
        # Setup mock IMAP connection
        mock_conn = Mock()
        mock_imap.return_value = mock_conn
        mock_conn.login.return_value = None
        mock_conn.select.return_value = ('OK', None)
        
        # Mock successful Gmail search
        mock_conn.search.return_value = ('OK', [b'1 2 3'])
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.gmail_config, f)
            config_file = f.name
        
        try:
            # Create sync instance with mocked OAuth2
            with patch('sync_mail.OAuth2Helper') as mock_oauth:
                mock_oauth_instance = Mock()
                mock_oauth_instance.authenticate_imap_oauth2.return_value = True
                mock_oauth.return_value = mock_oauth_instance
                
                sync = IMAPSync(config_file)
                
                # Test Gmail search
                criteria = {"gmail_query": "from:test@example.com after:2024/1/1"}
                messages = sync.search_emails(mock_conn, "INBOX", criteria, "imap.gmail.com")
                
                # Verify Gmail search was called
                mock_conn.search.assert_called_with(None, 'X-GM-RAW', '"from:test@example.com after:2024/1/1"')
                
                # Verify results
                self.assertEqual(len(messages), 3)
                self.assertEqual(messages, [b'1', b'2', b'3'])
                
        finally:
            os.unlink(config_file)
    
    @patch('sync_mail.imaplib.IMAP4_SSL') 
    def test_gmail_search_fallback(self, mock_imap):
        """Test Gmail search fallback to standard IMAP when X-GM-RAW fails."""
        # Setup mock IMAP connection
        mock_conn = Mock()
        mock_imap.return_value = mock_conn
        mock_conn.login.return_value = None
        mock_conn.select.return_value = ('OK', None)
        
        # Mock Gmail search failure, then standard search success
        mock_conn.search.side_effect = [
            ('NO', []),  # Gmail search fails
            ('OK', [b'4 5'])  # Standard search succeeds
        ]
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.gmail_config, f)
            config_file = f.name
        
        try:
            with patch('sync_mail.OAuth2Helper') as mock_oauth:
                mock_oauth_instance = Mock()
                mock_oauth_instance.authenticate_imap_oauth2.return_value = True
                mock_oauth.return_value = mock_oauth_instance
                
                sync = IMAPSync(config_file)
                
                # Test Gmail search with fallback
                criteria = {
                    "gmail_query": "from:test@example.com after:2024/1/1",
                    "subject": "Test Email",
                    "from": "test@example.com"
                }
                messages = sync.search_emails(mock_conn, "INBOX", criteria, "imap.gmail.com")
                
                # Verify both searches were attempted
                self.assertEqual(mock_conn.search.call_count, 2)
                
                # Verify fallback results
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages, [b'4', b'5'])
                
        finally:
            os.unlink(config_file)
    
    @patch('sync_mail.imaplib.IMAP4_SSL')
    def test_standard_imap_search(self, mock_imap):
        """Test standard IMAP search for non-Gmail servers."""
        # Setup mock IMAP connection
        mock_conn = Mock()
        mock_imap.return_value = mock_conn
        mock_conn.login.return_value = None
        mock_conn.select.return_value = ('OK', None)
        mock_conn.search.return_value = ('OK', [b'6 7 8 9'])
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.standard_config, f)
            config_file = f.name
        
        try:
            sync = IMAPSync(config_file)
            
            # Test standard search
            criteria = {
                "subject": "Test Email",
                "from": "sender@example.com",
                "date_after": "01-Jan-2024"
            }
            messages = sync.search_emails(mock_conn, "INBOX", criteria, "imap.outlook.com")
            
            # Verify standard IMAP search was used
            expected_search = 'SUBJECT "Test Email" FROM "sender@example.com" SINCE "01-Jan-2024"'
            mock_conn.search.assert_called_with(None, expected_search)
            
            # Verify results
            self.assertEqual(len(messages), 4)
            self.assertEqual(messages, [b'6', b'7', b'8', b'9'])
            
        finally:
            os.unlink(config_file)
    
    def test_gmail_query_examples(self):
        """Test various Gmail query examples for validity."""
        gmail_queries = [
            "from:sender@example.com",
            "subject:\"Important Message\"",
            "from:user@domain.com has:attachment",
            "after:2024/1/1 before:2024/12/31",
            "label:important -label:spam",
            "is:unread has:attachment",
            "category:updates OR category:social",
            "(from:a@b.com OR to:c@d.com) after:2024/6/1",
            "from:notifications@github.com -is:unread -label:archived"
        ]
        
        # All queries should be non-empty strings
        for query in gmail_queries:
            self.assertIsInstance(query, str)
            self.assertGreater(len(query), 0)
            self.assertNotIn('\n', query)  # Should be single line


def run_gmail_search_tests():
    """Run Gmail search tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    print("Running Gmail Search Tests...")
    print("=" * 50)
    run_gmail_search_tests()