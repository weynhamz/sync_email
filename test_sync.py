#!/usr/bin/env python3
"""
Test script for the email sync functionality.
This script tests the core functionality without requiring real IMAP credentials.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
from sync_mail import IMAPSync
from config_helper import validate_config, create_sample_config


class TestEmailSync(unittest.TestCase):
    """Test cases for email sync functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "source_mailbox": {
                "server": "test.server.com",
                "port": 993,
                "username": "test@example.com",
                "password": "testpass",
                "folder": "INBOX"
            },
            "target_mailbox": {
                "server": "target.server.com",
                "port": 993,
                "username": "target@example.com",
                "password": "targetpass",
                "folder": "INBOX"
            },
            "search_criteria": {
                "subject": "Test Email"
            },
            "log_level": "INFO",
            "dry_run": True
        }
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config)
        self.temp_config.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config should pass
        errors = validate_config(self.test_config)
        self.assertEqual(len(errors), 0)
        
        # Invalid config should fail
        invalid_config = self.test_config.copy()
        del invalid_config['source_mailbox']['username']
        errors = validate_config(invalid_config)
        self.assertGreater(len(errors), 0)
    
    def test_config_loading(self):
        """Test configuration file loading."""
        sync = IMAPSync(self.temp_config.name)
        self.assertEqual(sync.config['source_mailbox']['server'], 'test.server.com')
        self.assertEqual(sync.config['target_mailbox']['server'], 'target.server.com')
    
    def test_sample_config_creation(self):
        """Test sample configuration creation."""
        sample = create_sample_config()
        errors = validate_config(sample)
        self.assertEqual(len(errors), 0)
    
    @patch('sync_mail.imaplib.IMAP4_SSL')
    def test_imap_connection(self, mock_imap):
        """Test IMAP connection handling."""
        # Setup mock
        mock_conn = Mock()
        mock_imap.return_value = mock_conn
        mock_conn.login.return_value = None
        
        # Test connection
        sync = IMAPSync(self.temp_config.name)
        conn = sync.connect_imap(self.test_config['source_mailbox'])
        
        # Verify calls
        mock_imap.assert_called_once_with('test.server.com', 993)
        mock_conn.login.assert_called_once_with('test@example.com', 'testpass')
        self.assertEqual(conn, mock_conn)
    
    @patch('sync_mail.imaplib.IMAP4_SSL')
    def test_email_search(self, mock_imap):
        """Test email search functionality."""
        # Setup mock
        mock_conn = Mock()
        mock_imap.return_value = mock_conn
        mock_conn.login.return_value = None
        mock_conn.select.return_value = ('OK', None)
        mock_conn.search.return_value = ('OK', [b'1 2 3'])
        
        # Test search
        sync = IMAPSync(self.temp_config.name)
        conn = sync.connect_imap(self.test_config['source_mailbox'])
        messages = sync.search_emails(conn, 'INBOX', {'subject': 'Test'})
        
        # Verify results
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages, [b'1', b'2', b'3'])
        mock_conn.search.assert_called_once()
    
    def test_header_decoding(self):
        """Test email header decoding."""
        sync = IMAPSync(self.temp_config.name)
        
        # Test simple string
        result = sync._decode_header("Simple Subject")
        self.assertEqual(result, "Simple Subject")
        
        # Test empty string
        result = sync._decode_header("")
        self.assertEqual(result, "")
        
        # Test None
        result = sync._decode_header(None)
        self.assertEqual(result, "")


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    print("Running Email Sync Tests...")
    print("=" * 50)
    run_tests()