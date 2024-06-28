#!/bin/bash

# Ensure script exits if any command fails
set -e

# Clean any existing coverage data
coverage erase

# Run tests with coverage
# coverage run -m pytest
coverage run --source=services -m unittest discover -s tests

# Generate reports
coverage report
coverage html
coverage xml

# Check if the coverage report exists
if [ ! -f "coverage.xml" ]; then
  echo "Coverage report not found!"
  exit 1
fi

# Send the coverage report to Coveralls
# Ensure you have installed the coveralls-python package
pip install coveralls

# Export the Coveralls repository token
export COVERALLS_REPO_TOKEN=owGR8cn5uu9HvdWxjp3Z8ORm1CMcjlBbI

# Upload the coverage report to Coveralls
coveralls

echo "Coverage report sent to Coveralls"