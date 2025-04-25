#!/bin/bash

# Quick start script for AI Interview application using in-memory database

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Interview Platform - Quick Start (Memory DB) ===${NC}"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }
fi

# Create required directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p uploads instance static/uploads

# Set correct permissions
echo -e "${GREEN}Setting correct permissions...${NC}"
chmod -R 777 instance uploads static/uploads

# Create a temporary env file for testing with in-memory database
echo -e "${GREEN}Setting up environment...${NC}"
cat > .env << EOL
# Flask configuration
SECRET_KEY=test-key
DATABASE_URI=sqlite:///:memory:

# Gemini API key (fake key for development)
GEMINI_API_KEY=AIzaSyA7zgkfPqewfQsGhQi7L8OYVxsiZuOguSU
EOL

# Run the application with in-memory database
# We'll use seed_data.py to populate the database on first run
echo -e "${GREEN}Starting the application...${NC}"
echo -e "${BLUE}Access the application at http://localhost:8080${NC}"
echo -e "${BLUE}NOTE: The database is in-memory, all data will be lost when the application stops${NC}"

# Set environment variable to tell app to seed the database on startup
export SEED_DATABASE=1
# Use port 8080 to avoid macOS AirPlay Receiver conflict on port 5000
export FLASK_RUN_PORT=8080
python app.py