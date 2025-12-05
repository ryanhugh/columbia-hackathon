#!/bin/bash

# PolyIntel Local Development Start Script
# Starts both backend and frontend in one command

set -e

echo "================================"
echo "PolyIntel Local Setup"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    echo "Download from: https://nodejs.org"
    exit 1
fi

# Check if Python 3.12+ is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.12+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
echo ""

# Setup Backend
echo -e "${YELLOW}Setting up Backend...${NC}"
cd "$SCRIPT_DIR/polyintel"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found!${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
    fi
    echo -e "${YELLOW}Created .env file. Please add your API keys before running.${NC}"
    echo ""
    echo "Edit: $SCRIPT_DIR/polyintel/.env"
    exit 1
fi

pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Setup Frontend
echo ""
echo -e "${YELLOW}Setting up Frontend...${NC}"
cd "$SCRIPT_DIR/polyintel-ui"

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies (this may take a minute)..."
    npm install
fi

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    fi
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Summary
echo ""
echo "================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}To start the application:${NC}"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd $SCRIPT_DIR/polyintel"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd $SCRIPT_DIR/polyintel-ui"
echo "  npm run dev"
echo ""
echo -e "${GREEN}Then open:${NC}"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
