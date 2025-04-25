#!/bin/bash

# AI Interview Platform Setup and Run Script

# Colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Interview Platform Setup ===${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${NC}"; exit 1; }

# Check if .env file exists, create it if not
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cat > .env << EOL
# Flask configuration
SECRET_KEY=development-key-replace-in-production
DATABASE_URI=sqlite:///instance/ai_interview.db

# Gemini API key
GEMINI_API_KEY=AIzaSyA7zgkfPqewfQsGhQi7L8OYVxsiZuOguSU
EOL
fi

# Create required directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p uploads instance static/uploads

# Set correct permissions on the instance directory
echo -e "${GREEN}Setting correct permissions...${NC}"
chmod -R 777 instance

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt || { echo -e "${RED}Failed to install dependencies${NC}"; exit 1; }

# Initialize and seed the database
echo -e "${GREEN}Initializing database...${NC}"
python seed_data.py || { 
    echo -e "${YELLOW}Warning: Database initialization might have encountered issues.${NC}"
    echo -e "${YELLOW}Continuing anyway... The app will create the necessary tables on startup.${NC}"
}

# Run the application
echo -e "${GREEN}Starting AI Interview Platform...${NC}"
echo -e "${BLUE}Access the application at http://localhost:5000${NC}"
python app.py