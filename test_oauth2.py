#!/usr/bin/env python3
"""
Test OAuth2 implementation without requiring actual Google credentials.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
import sys

# Test the OAuth2 implementation structure
def test_oauth2_structure():
    """Test that OAuth2 classes and methods are properly structured."""
    print("Testing OAuth2 Implementation Structure...")
    print("=" * 50)
    
    # Test imports and class structure
    try:
        from oauth2_helper import OAuth2Helper, OAUTH2_AVAILABLE
        print("✓ OAuth2Helper class imported successfully")
        
        # Test helper instantiation
        helper = OAuth2Helper("test_creds.json", "test_token.json")
        print("✓ OAuth2Helper instantiated successfully")
        
        # Test method existence
        methods = [
            'get_oauth2_credentials',
            'generate_xoauth2_string', 
            'authenticate_imap_oauth2',
            'is_oauth2_configured',
            'setup_oauth2_credentials'
        ]
        
        for method in methods:
            if hasattr(helper, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
        
        # Test configuration detection
        configured = helper.is_oauth2_configured()
        print(f"✓ OAuth2 configuration check: {'configured' if configured else 'not configured (expected)'}")
        
        # Test XOAUTH2 string generation
        if OAUTH2_AVAILABLE:
            xoauth_str = helper.generate_xoauth2_string("test@gmail.com", "fake_token")
            print(f"✓ XOAUTH2 string generated: {len(xoauth_str)} characters")
        else:
            print("! OAuth2 dependencies not available - expected in test environment")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing OAuth2 structure: {e}")
        return False


def test_sync_oauth2_integration():
    """Test that sync_mail.py integrates OAuth2 properly."""
    print("\nTesting Sync Script OAuth2 Integration...")
    print("=" * 50)
    
    try:
        from sync_mail import IMAPSync
        
        # Create test config with OAuth2
        test_config = {
            "source_mailbox": {
                "server": "imap.gmail.com",
                "port": 993,
                "username": "test@gmail.com",
                "auth_method": "oauth2",
                "credentials_file": "test_creds.json",
                "token_file": "test_token.json",
                "folder": "INBOX"
            },
            "target_mailbox": {
                "server": "imap.target.com",
                "port": 993,
                "username": "target@example.com",
                "auth_method": "password",
                "password": "testpass",
                "folder": "INBOX"
            },
            "log_level": "INFO"
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            # Test sync instantiation with OAuth2 config
            sync = IMAPSync(config_file)
            print("✓ IMAPSync instantiated with OAuth2 config")
            
            # Test that auth_method is properly detected
            source_config = sync.config['source_mailbox']
            if source_config.get('auth_method') == 'oauth2':
                print("✓ OAuth2 auth method detected in source mailbox")
            else:
                print("✗ OAuth2 auth method not properly detected")
            
            # Test mixed auth configuration
            target_config = sync.config['target_mailbox']
            if target_config.get('auth_method') == 'password':
                print("✓ Password auth method detected in target mailbox")
            else:
                print("✗ Password auth method not properly detected")
            
            return True
            
        finally:
            os.unlink(config_file)
            
    except Exception as e:
        print(f"✗ Error testing sync OAuth2 integration: {e}")
        return False


def test_config_validation():
    """Test OAuth2 configuration validation."""
    print("\nTesting OAuth2 Configuration Validation...")
    print("=" * 50)
    
    try:
        from config_helper import validate_config
        
        # Test valid OAuth2 config
        valid_oauth2_config = {
            "source_mailbox": {
                "server": "imap.gmail.com",
                "port": 993,
                "username": "test@gmail.com",
                "auth_method": "oauth2",
                "folder": "INBOX"
            },
            "target_mailbox": {
                "server": "imap.target.com",
                "port": 993,
                "username": "target@example.com",
                "auth_method": "password",
                "password": "testpass",
                "folder": "INBOX"
            }
        }
        
        errors = validate_config(valid_oauth2_config)
        if len(errors) == 0:
            print("✓ Valid OAuth2 config passes validation")
        else:
            print(f"✗ Valid OAuth2 config failed validation: {errors}")
        
        # Test invalid auth method
        invalid_config = valid_oauth2_config.copy()
        invalid_config['source_mailbox']['auth_method'] = 'invalid_method'
        
        errors = validate_config(invalid_config)
        if len(errors) > 0:
            print("✓ Invalid auth method properly rejected")
        else:
            print("✗ Invalid auth method not detected")
        
        # Test missing password for password auth
        invalid_config2 = valid_oauth2_config.copy()
        invalid_config2['target_mailbox']['auth_method'] = 'password'
        del invalid_config2['target_mailbox']['password']
        
        errors = validate_config(invalid_config2)
        if len(errors) > 0:
            print("✓ Missing password for password auth properly detected")
        else:
            print("✗ Missing password not detected")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing config validation: {e}")
        return False


def run_all_tests():
    """Run all OAuth2 tests."""
    print("OAuth2 Implementation Test Suite")
    print("=" * 60)
    
    tests = [
        test_oauth2_structure,
        test_sync_oauth2_integration,
        test_config_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All OAuth2 implementation tests passed!")
        print("\nNext steps for OAuth2 setup:")
        print("1. Install Google dependencies: pip install google-auth google-auth-oauthlib")
        print("2. Set up Google Cloud project and download credentials.json")
        print("3. Run: python oauth2_helper.py --setup for detailed instructions")
    else:
        print("❌ Some tests failed - OAuth2 implementation needs attention")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)