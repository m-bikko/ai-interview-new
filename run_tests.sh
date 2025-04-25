#!/bin/bash

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Interview Platform Tests ===${NC}"

# Create required directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p uploads instance static/uploads

# Set correct permissions on the instance directory
echo -e "${GREEN}Setting correct permissions...${NC}"
chmod -R 777 instance

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }
fi

# Run the tests
echo -e "${GREEN}Running tests...${NC}"
python tests.py

# Check test result
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Please check the output above for details.${NC}"
    exit 1
fi