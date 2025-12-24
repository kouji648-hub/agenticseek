#!/bin/bash

# AgenticSeek Backend Server Startup Script

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting AgenticSeek Backend Server..."
echo "📍 Project Root: $PROJECT_ROOT"
echo "📍 Server Directory: $SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$PROJECT_ROOT/venv"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Set environment variables
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-d8d78811ea69434fad5d447b5c1027e3}"
export PORT="${PORT:-7777}"

# Start the server
echo "✅ Starting API server on port $PORT..."
cd "$PROJECT_ROOT"
python "$SCRIPT_DIR/api.py"
