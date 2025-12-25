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

echo -e "${BLUE}🚀 AgenticSeek 開発環境${NC}"
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
        echo -e "${YELLOW}⚠️  ポート $port は使用中です。次のポート $((port+1)) を試します...${NC}"
        port=$((port+1))
        if [ $port -gt $((start_port+100)) ]; then
            echo -e "${RED}❌ 利用可能なポートが見つかりませんでした${NC}"
            return 1
        fi
    done

    echo $port
}

# Check for required tools
echo -e "${BLUE}📋 必要なツールを確認中...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js がインストールされていません${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 がインストールされていません${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js と Python 3 がインストールされています${NC}"
echo ""

# Find available ports
echo -e "${BLUE}🔍 利用可能なポートを検索中...${NC}"

FRONTEND_PORT=$(find_available_port 5173)
if [ $? -ne 0 ]; then
    exit 1
fi

BACKEND_PORT=$(find_available_port 7777)
if [ $? -ne 0 ]; then
    exit 1
fi

echo -e "${GREEN}✅ フロントエンドポート: $FRONTEND_PORT${NC}"
echo -e "${GREEN}✅ バックエンドポート: $BACKEND_PORT${NC}"
echo ""

# Start backend server
echo -e "${BLUE}🔧 バックエンドAPIサーバーを起動中...${NC}"

# Create a temporary directory for logs
LOG_DIR="/tmp/agenticseek-logs"
mkdir -p "$LOG_DIR"

BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Start backend in background
cd "$SCRIPT_DIR"

# Create Python virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}📦 Python仮想環境を作成中...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install/update dependencies
echo -e "${YELLOW}📥 Python依存関係をインストール中...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/server/requirements.txt" > /dev/null 2>&1

# Install Playwright browsers (Firefox)
echo -e "${YELLOW}🦊 Playwright (Firefox) をインストール中...${NC}"
playwright install firefox > /dev/null 2>&1

# Set environment variables
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-d8d78811ea69434fad5d447b5c1027e3}"
export PORT=$BACKEND_PORT

# Start backend server
nohup python "$SCRIPT_DIR/server/api.py" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ バックエンドAPIサーバーが起動しました (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}   📍 URL: http://localhost:$BACKEND_PORT${NC}"
echo ""

# Wait for backend to be ready
echo -e "${YELLOW}⏳ バックエンドAPIの準備を待機中...${NC}"
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ バックエンドAPIの起動に失敗しました${NC}"
    echo -e "${RED}   ログを確認してください: $BACKEND_LOG${NC}"
    exit 1
fi

# Start frontend server
echo -e "${BLUE}🎨 フロントエンド開発サーバーを起動中...${NC}"

# Update environment variable for frontend
export VITE_API_BASE_URL="http://localhost:$BACKEND_PORT"

nohup npm run dev -- --port $FRONTEND_PORT --host > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ フロントエンド開発サーバーが起動しました (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}   📍 URL: http://localhost:$FRONTEND_PORT${NC}"
echo ""

# Wait for frontend to be ready
echo -e "${YELLOW}⏳ フロントエンドの準備を待機中...${NC}"
sleep 3

# Display summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✨ AgenticSeek が起動しました！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}📍 アクセスURL:${NC}"
echo -e "   🌐 フロントエンド: http://localhost:$FRONTEND_PORT"
echo -e "   🔧 バックエンドAPI: http://localhost:$BACKEND_PORT"
echo -e "   📚 APIドキュメント: http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${YELLOW}📝 ログファイル:${NC}"
echo -e "   フロントエンド: $FRONTEND_LOG"
echo -e "   バックエンド: $BACKEND_LOG"
echo ""
echo -e "${YELLOW}🎯 プロセスID:${NC}"
echo -e "   フロントエンド PID: $FRONTEND_PID"
echo -e "   バックエンド PID: $BACKEND_PID"
echo ""
echo -e "${YELLOW}🛑 停止方法:${NC}"
echo -e "   kill $FRONTEND_PID  # フロントエンド停止"
echo -e "   kill $BACKEND_PID   # バックエンド停止"
echo -e "   または Ctrl+C を押してください"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 サーバーを停止中...${NC}"

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ フロントエンドを停止しました${NC}"
    fi

    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ バックエンドを停止しました${NC}"
    fi

    echo -e "${GREEN}✅ クリーンアップ完了${NC}"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Open browser
echo -e "${BLUE}🌐 ブラウザを開いています...${NC}"
sleep 2

# Try to open in Google Chrome, fallback to default browser
if open -a "Google Chrome" "http://localhost:$FRONTEND_PORT" 2>/dev/null; then
    echo -e "${GREEN}✅ Google Chrome でブラウザを開きました${NC}"
else
    open "http://localhost:$FRONTEND_PORT"
    echo -e "${GREEN}✅ デフォルトブラウザで開きました${NC}"
fi

echo ""
echo -e "${YELLOW}💡 このウィンドウは開いたままにしてください。${NC}"
echo -e "${YELLOW}   終了する場合は Ctrl+C を押すか、ウィンドウを閉じてください。${NC}"
echo ""

# Keep the script running
wait
