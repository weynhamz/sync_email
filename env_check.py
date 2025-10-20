#!/usr/bin/env python3
"""
Environment check utility for Email Sync Project
Provides information about the current Python environment and dependencies.
"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("   ❌ Python 3.8+ required")
        return False
    else:
        print("   ✅ Version OK")
        return True


def check_virtual_environment():
    """Check virtual environment status."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    print(f"📦 Virtual Environment: {'Active' if in_venv else 'Not Active'}")
    
    if in_venv:
        print(f"   📁 Path: {sys.prefix}")
        print("   ✅ Using virtual environment")
    else:
        if Path('venv').exists():
            print("   ⚠️  Virtual environment found but not activated")
            print("   💡 Run: source venv/bin/activate (Linux/macOS) or venv\\Scripts\\activate (Windows)")
        else:
            print("   ❌ No virtual environment detected")
            print("   💡 Run: ./setup.sh or python -m venv venv")
    
    return in_venv


def check_dependencies():
    """Check if required dependencies are installed."""
    print("📚 Dependencies:")
    
    required_packages = [
        'imaplib2',
        'email-validator',
        'python-dotenv'
    ]
    
    optional_packages = [
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (required)")
            all_good = False
    
    oauth_available = True
    for package in optional_packages:
        try:
            if package == 'google-auth':
                import google.auth
            elif package == 'google-auth-oauthlib':
                import google_auth_oauthlib
            elif package == 'google-auth-httplib2':
                import google.auth.httplib2
            print(f"   ✅ {package} (optional - OAuth2)")
        except ImportError:
            print(f"   ⚠️  {package} (optional - OAuth2)")
            oauth_available = False
    
    if oauth_available:
        print("   🔐 OAuth2 support: Available")
    else:
        print("   🔐 OAuth2 support: Not available (install google-auth packages)")
    
    return all_good


def check_configuration():
    """Check configuration files."""
    print("⚙️  Configuration:")
    
    config_files = ['config.json', 'config.example.json', 'config.oauth2.example.json']
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file}")
    
    if Path('config.json').exists():
        try:
            # Try to validate config
            result = subprocess.run([sys.executable, 'config_helper.py', 'validate'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ Configuration is valid")
            else:
                print("   ❌ Configuration has errors")
                print(f"      {result.stderr.strip()}")
        except Exception as e:
            print(f"   ⚠️  Could not validate config: {e}")
    else:
        print("   ⚠️  No config.json found - copy from example file")


def check_oauth2_setup():
    """Check OAuth2 setup."""
    print("🔐 OAuth2 Setup:")
    
    credentials_file = Path('credentials.json')
    token_file = Path('token.json')
    
    if credentials_file.exists():
        print("   ✅ credentials.json found")
    else:
        print("   ❌ credentials.json not found")
        print("   💡 Download from Google Cloud Console")
    
    if token_file.exists():
        print("   ✅ token.json found (OAuth2 authorized)")
    else:
        print("   ⚠️  token.json not found (need to authorize)")
        print("   💡 Run sync script to start OAuth2 flow")


def check_project_files():
    """Check that main project files exist."""
    print("📄 Project Files:")
    
    required_files = [
        'sync_mail.py',
        'oauth2_helper.py',
        'config_helper.py',
        'requirements.txt'
    ]
    
    all_present = True
    
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name}")
            all_present = False
    
    return all_present


def run_quick_test():
    """Run a quick functionality test."""
    print("🧪 Quick Test:")
    
    try:
        # Test main script help
        result = subprocess.run([sys.executable, 'sync_mail.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Main script functional")
        else:
            print("   ❌ Main script has issues")
            return False
        
        # Test OAuth2 helper
        result = subprocess.run([sys.executable, 'oauth2_helper.py', '--setup'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ OAuth2 helper functional")
        else:
            print("   ❌ OAuth2 helper has issues")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def print_recommendations():
    """Print recommendations based on checks."""
    print("\n💡 Recommendations:")
    
    # Check if venv exists but not active
    if Path('venv').exists() and not (hasattr(sys, 'real_prefix') or 
                                     (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("   1. Activate virtual environment: source venv/bin/activate")
    
    # Check if setup hasn't been run
    if not Path('venv').exists():
        print("   1. Run automated setup: ./setup.sh")
    
    # Check if config doesn't exist
    if not Path('config.json').exists():
        print("   2. Create configuration: cp config.example.json config.json")
        print("   3. Edit config.json with your IMAP settings")
    
    # Check for OAuth2 setup
    if not Path('credentials.json').exists():
        print("   4. For Gmail OAuth2: Follow OAUTH2_SETUP.md guide")
    
    print("   5. Test setup: python sync_mail.py --dry-run")


def main():
    """Main check routine."""
    print("🔍 Email Sync Project Environment Check")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_dependencies(),
        check_project_files(),
    ]
    
    print()
    check_configuration()
    print()
    check_oauth2_setup()
    print()
    
    # Only run quick test if basic checks pass
    if all(checks):
        test_passed = run_quick_test()
    else:
        test_passed = False
    
    print("\n" + "=" * 50)
    
    if all(checks) and test_passed:
        print("🎉 Environment check passed! Project is ready to use.")
    else:
        print("⚠️  Some issues found. See recommendations below.")
    
    print_recommendations()


if __name__ == "__main__":
    main()