#!/bin/bash

echo "Running Black..."
black .

echo "Running Flake8..."
flake8 .

echo "Running Mypy..."
mypy .

echo "Running pytest..."
PYTHONPATH=. pytest

# If any command failed, exit with a non-zero status
if [ $? -ne 0 ]; then
    echo "Linting failed. Please fix the issues before committing."
    exit 1
fi