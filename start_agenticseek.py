#!/usr/bin/env python3
import subprocess
import time
import webbrowser
import os

AGENTICSEEK_DIR = "/Users/kawabatakouji/agenticseek"

print("🚀 AgenticSeekを起動しています...\n")

# サーバー起動
print("⏳ バックエンドを起動中...")
server_dir = os.path.join(AGENTICSEEK_DIR, "server")
server_proc = subprocess.Popen(["python", "api.py"], cwd=server_dir)

# フロントエンド起動
print("⏳ フロントエンドを起動中...")
frontend_proc = subprocess.Popen(["npm", "start"], cwd=AGENTICSEEK_DIR)

# ブラウザ起動
time.sleep(3)
print("🌐 ブラウザを開いています...")
webbrowser.open("http://localhost:3000")

print("\n✅ AgenticSeekが起動しました！")
print("   フロントエンド: http://localhost:3000")
print("   停止: Ctrl+C を押してください\n")

try:
    server_proc.wait()
except KeyboardInterrupt:
    print("⏹ 停止中...")
    server_proc.terminate()
    frontend_proc.terminate()
