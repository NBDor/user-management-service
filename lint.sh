#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to handle errors
handle_error() {
    echo -e "\n${RED}$1 failed. Please fix the issues before committing.${NC}"
    exit 1
}

# Format with Black
print_section "Running Black..."
black . || handle_error "Black formatting"

# Run Flake8
print_section "Running Flake8..."
flake8 . || handle_error "Flake8 check"

# Run Mypy
print_section "Running Mypy..."
PYTHONPATH=. mypy app || handle_error "Mypy type checking"

# # Run Pytest
print_section "Running Pytest..."
PYTHONPATH=. pytest || handle_error "Pytest"

# If we get here, everything passed
echo -e "\n${GREEN}All checks passed successfully!${NC}"