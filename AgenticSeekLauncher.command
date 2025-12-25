#!/bin/bash

# AgenticSeek Launcher for macOS
# Double-click this file to start the development environment

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make the start script executable
chmod +x "$SCRIPT_DIR/start-dev.sh"

# Run the start script
"$SCRIPT_DIR/start-dev.sh"
