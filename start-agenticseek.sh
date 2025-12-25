#!/bin/bash

# AgenticSeek 自動起動スクリプト
AGENTICSEEK_DIR="/Users/kawabatakouji/agenticseek"

echo "🚀 AgenticSeekを起動しています..."
cd "$AGENTICSEEK_DIR" || exit 1

# バックエンド起動
cd server && python api.py &
SERVER_PID=$!

# フロントエンド起動
cd .. && npm start &
FRONTEND_PID=$!

# ブラウザを開く
sleep 3
open "http://localhost:3000"

echo "✅ AgenticSeekが起動しました！"
wait
