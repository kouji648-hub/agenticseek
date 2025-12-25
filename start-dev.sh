#!/bin/bash

# AgenticSeek Development Environment Startup Script
# This script starts both the frontend and backend servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}🚀 AgenticSeek Development Environment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=$1
    local port=$start_port
    
    while check_port $port; do
        echo -e "${YELLOW}⚠️  Port $port is in use, trying $((port+1))...${NC}"
        port=$((port+1))
        if [ $port -gt $((start_port+100)) ]; then
            echo -e "${RED}❌ Could not find available port${NC}"
            return 1
        fi
    done
    
    echo $port
}

# Check for required tools
echo -e "${BLUE}📋 Checking requirements...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js and Python 3 are installed${NC}"
echo ""

# Find available ports
echo -e "${BLUE}🔍 Finding available ports...${NC}"

FRONTEND_PORT=$(find_available_port 3000)
if [ $? -ne 0 ]; then
    exit 1
fi

BACKEND_PORT=$(find_available_port 7777)
if [ $? -ne 0 ]; then
    exit 1
fi

echo -e "${GREEN}✅ Frontend port: $FRONTEND_PORT${NC}"
echo -e "${GREEN}✅ Backend port: $BACKEND_PORT${NC}"
echo ""

# Start backend server
echo -e "${BLUE}🔧 Starting Backend API Server...${NC}"

# Create a temporary directory for logs
LOG_DIR="/tmp/agenticseek-logs"
mkdir -p "$LOG_DIR"

BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Start backend in background
cd "$SCRIPT_DIR"

# Create Python virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install/update dependencies
echo -e "${YELLOW}📥 Installing Python dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/server/requirements.txt" > /dev/null 2>&1

# Install Playwright browsers
echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
playwright install chromium > /dev/null 2>&1

# Set environment variables
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-d8d78811ea69434fad5d447b5c1027e3}"
export PORT=$BACKEND_PORT

# Start backend server
nohup python "$SCRIPT_DIR/server/api.py" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Backend API Server started (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}   📍 URL: http://localhost:$BACKEND_PORT${NC}"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for Backend API to be ready...${NC}"
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend API failed to start${NC}"
    echo -e "${RED}   Check logs: $BACKEND_LOG${NC}"
    exit 1
fi

# Start frontend server
echo -e "${BLUE}🔧 Starting Frontend Development Server...${NC}"

# Update environment variable for frontend
export VITE_API_BASE_URL="http://localhost:$BACKEND_PORT"

nohup npm run dev -- --port $FRONTEND_PORT > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Frontend Development Server started (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}   📍 URL: http://localhost:$FRONTEND_PORT${NC}"
echo ""

# Display summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ AgenticSeek Development Environment Ready!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Frontend:${NC}"
echo -e "  🌐 URL: http://localhost:$FRONTEND_PORT"
echo -e "  📝 Logs: $FRONTEND_LOG"
echo ""
echo -e "${YELLOW}Backend API:${NC}"
echo -e "  🌐 URL: http://localhost:$BACKEND_PORT"
echo -e "  📚 Docs: http://localhost:$BACKEND_PORT/docs"
echo -e "  📝 Logs: $BACKEND_LOG"
echo ""
echo -e "${YELLOW}Processes:${NC}"
echo -e "  Frontend PID: $FRONTEND_PID"
echo -e "  Backend PID: $BACKEND_PID"
echo ""
echo -e "${YELLOW}To stop the servers:${NC}"
echo -e "  kill $FRONTEND_PID  # Stop frontend"
echo -e "  kill $BACKEND_PID   # Stop backend"
echo -e "  Or press Ctrl+C to stop this script"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Keep the script running
wait
