#!/usr/bin/env python3
"""
Configuration validation and helper utilities for the email sync project.
"""

import json
import sys
from typing import Dict, ListT
import logging


def validate_config(config: Dict) -> List[str]:
    """
    Validate the configuration file and return a list of errors.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Required top-level keys
    required_keys = ['source_mailbox', 'target_mailbox']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required configuration key: {key}")
    
    # Validate mailbox configurations
    for mailbox_type in ['source_mailbox', 'target_mailbox']:
        if mailbox_type in config:
            mailbox_config = config[mailbox_type]
            required_mailbox_keys = ['server', 'username', 'password']
            
            for key in required_mailbox_keys:
                if key not in mailbox_config:
                    errors.append(f"Missing required key '{key}' in {mailbox_type}")
            
            # Validate port if specified
            if 'port' in mailbox_config:
                try:
                    port = int(mailbox_config['port'])
                    if port < 1 or port > 65535:
                        errors.append(f"Invalid port number in {mailbox_type}: {port}")
                except (ValueError, TypeError):
                    errors.append(f"Port must be a number in {mailbox_type}")
    
    # Validate log level if specified
    if 'log_level' in config:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config['log_level'].upper() not in valid_levels:
            errors.append(f"Invalid log_level: {config['log_level']}. Must be one of {valid_levels}")
    
    return errors


def create_sample_config() -> Dict:
    """Create a sample configuration dictionary."""
    return {
        "source_mailbox": {
            "server": "imap.gmail.com",
            "port": 993,
            "username": "source@gmail.com",
            "password": "your_app_password",
            "folder": "INBOX"
        },
        "target_mailbox": {
            "server": "imap.outlook.com",
            "port": 993,
            "username": "target@outlook.com",
            "password": "your_password", 
            "folder": "INBOX"
        },
        "search_criteria": {
            "subject": "Test Email",
            "from": "sender@example.com",
            "date_after": "01-Jan-2024"
        },
        "log_level": "INFO",
        "dry_run": True
    }


def main():
    """CLI utility for config management."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "validate":
            config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                errors = validate_config(config)
                if errors:
                    print(f"Configuration errors in {config_file}:")
                    for error in errors:
                        print(f"  - {error}")
                    sys.exit(1)
                else:
                    print(f"Configuration {config_file} is valid!")
                    
            except FileNotFoundError:
                print(f"Configuration file {config_file} not found")
                sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"Error parsing {config_file}: {e}")
                sys.exit(1)
                
        elif command == "create":
            config_file = sys.argv[2] if len(sys.argv) > 2 else "config.json"
            sample_config = create_sample_config()
            
            try:
                with open(config_file, 'w') as f:
                    json.dump(sample_config, f, indent=2)
                print(f"Sample configuration created: {config_file}")
                print("Please edit the file with your actual IMAP settings.")
            except Exception as e:
                print(f"Error creating config file: {e}")
                sys.exit(1)
        else:
            print("Unknown command. Use 'validate' or 'create'")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python config_helper.py validate [config_file]")
        print("  python config_helper.py create [config_file]")


if __name__ == "__main__":
    main()