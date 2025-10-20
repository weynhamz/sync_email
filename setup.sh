#!/bin/bash
# Email Sync Project Setup Script
# This script sets up a complete development environment with virtual environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
PYTHON_MIN_VERSION="3.8"

echo -e "${BLUE}Email Sync Project Setup${NC}"
echo "=========================="

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python $PYTHON_MIN_VERSION or later."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_info "Found Python $PYTHON_VERSION"
    
    # Basic version check (this is a simplified check)
    if [[ $(echo "$PYTHON_VERSION < $PYTHON_MIN_VERSION" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
        print_warning "Python $PYTHON_VERSION detected. Python $PYTHON_MIN_VERSION+ recommended."
    fi
}

# Create virtual environment
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment '$VENV_NAME' already exists."
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_NAME"
            print_info "Removed existing virtual environment."
        else
            print_info "Using existing virtual environment."
            return
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_NAME"
    print_success "Virtual environment created: $VENV_NAME"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source "$VENV_NAME/Scripts/activate"
        ACTIVATION_SCRIPT="$VENV_NAME\\Scripts\\activate"
    else
        # Unix/Linux/macOS
        source "$VENV_NAME/bin/activate"
        ACTIVATION_SCRIPT="$VENV_NAME/bin/activate"
    fi
    
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_info "Installing dependencies..."
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install main dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Main dependencies installed from requirements.txt"
    else
        print_warning "requirements.txt not found"
    fi
    
    # Install development dependencies if available
    if [ -f "requirements-dev.txt" ]; then
        read -p "Install development dependencies? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            pip install -r requirements-dev.txt
            print_success "Development dependencies installed from requirements-dev.txt"
        fi
    fi
}

# Create configuration files
setup_config() {
    print_info "Setting up configuration files..."
    
    if [ ! -f "config.json" ]; then
        if [ -f "config.example.json" ]; then
            cp config.example.json config.json
            print_success "Created config.json from example"
            print_warning "Please edit config.json with your IMAP settings"
        elif [ -f "config.oauth2.example.json" ]; then
            cp config.oauth2.example.json config.json
            print_success "Created config.json from OAuth2 example"
            print_warning "Please edit config.json with your email settings"
        fi
    else
        print_info "config.json already exists"
    fi
}

# Validate setup
validate_setup() {
    print_info "Validating setup..."
    
    # Check if virtual environment is active
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment is active: $VIRTUAL_ENV"
    else
        print_warning "Virtual environment not detected"
    fi
    
    # Test Python imports
    if python -c "import imaplib, email, json" &> /dev/null; then
        print_success "Core Python modules available"
    else
        print_error "Core Python modules missing"
    fi
    
    # Test OAuth2 dependencies (optional)
    if python -c "import google.auth" &> /dev/null; then
        print_success "OAuth2 dependencies available"
    else
        print_info "OAuth2 dependencies not installed (optional)"
    fi
    
    # Test configuration
    if [ -f "config.json" ]; then
        if python config_helper.py validate &> /dev/null; then
            print_success "Configuration file is valid"
        else
            print_warning "Configuration file needs attention"
        fi
    fi
    
    # Test main script
    if python sync_mail.py --help &> /dev/null; then
        print_success "Main script is functional"
    else
        print_error "Main script has issues"
    fi
}

# Print usage instructions
print_usage() {
    echo
    echo -e "${GREEN}Setup Complete!${NC}"
    echo "================"
    echo
    echo "To use the email sync tool:"
    echo
    echo "1. Activate the virtual environment:"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "   ${BLUE}$ACTIVATION_SCRIPT${NC}"
    else
        echo -e "   ${BLUE}source $ACTIVATION_SCRIPT${NC}"
    fi
    echo
    echo "2. Edit configuration:"
    echo -e "   ${BLUE}nano config.json${NC}  # or use your preferred editor"
    echo
    echo "3. Run the sync tool:"
    echo -e "   ${BLUE}python sync_mail.py --dry-run${NC}  # Test run"
    echo -e "   ${BLUE}python sync_mail.py${NC}             # Actual sync"
    echo
    echo "For OAuth2 setup (Gmail):"
    echo -e "   ${BLUE}python oauth2_helper.py --setup${NC}"
    echo
    echo "For help:"
    echo -e "   ${BLUE}python sync_mail.py --help${NC}"
    echo
}

# Main setup process
main() {
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_config
    validate_setup
    print_usage
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi