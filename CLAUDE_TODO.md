# Claude Code - 完全な作業リスト

## 🎯 目標

Mac ローカル環境で AgenticSeek を完全に動作させる

---

## 📋 実施すべき作業（優先度順）

### Phase 1: ファイル転送と初期セットアップ（最優先）

#### タスク 1.1: Manus から Mac へファイルをコピー

**実施内容:**

Manus プロジェクト（`/home/ubuntu/agenticseek-frontend`）から Mac（`~/agenticseek`）へ以下をコピー：

```
コピー元: /home/ubuntu/agenticseek-frontend/server/
コピー先: ~/agenticseek/server/

ファイル:
- api.py
- requirements.txt
- start.sh
- README.md
```

**方法:**

Mac のターミナルで以下を実行（Manus サーバーにアクセス可能な場合）：

```bash
# Manus サーバーから直接コピー（SSH経由）
scp -r ubuntu@<manus-server>:/home/ubuntu/agenticseek-frontend/server/* ~/agenticseek/server/
```

**または手動でダウンロード:**

1. Manus の Management UI を開く
2. **Code** パネルで以下をダウンロード：
   - `server/api.py`
   - `server/requirements.txt`
   - `server/start.sh`
   - `server/README.md`
3. `~/agenticseek/server/` に保存

**確認:**
```bash
ls -la ~/agenticseek/server/
# 以下が表示されることを確認:
# - api.py
# - requirements.txt
# - start.sh
# - README.md
```

---

#### タスク 1.2: ファイルのパーミッション設定

```bash
cd ~/agenticseek/server
chmod +x start.sh
chmod +x api.py
```

---

#### タスク 1.3: GitHub にプッシュ

```bash
cd ~/agenticseek

# ファイルを追加
git add server/
git add start-dev.sh
git add *.md

# コミット
git commit -m "Add backend API server and setup scripts"

# プッシュ
git push origin main

# 確認
git log --oneline -5
```

---

### Phase 2: 依存関係のインストール

#### タスク 2.1: Python 依存関係をインストール

```bash
cd ~/agenticseek
source venv/bin/activate

# requirements.txt をインストール
pip install -r server/requirements.txt

# Playwright ブラウザをインストール
playwright install chromium

# 確認
pip list | grep -E "fastapi|uvicorn|playwright"
```

**期待される出力:**
```
fastapi                    0.104.1
uvicorn                    0.24.0
playwright                 1.40.0
```

---

#### タスク 2.2: Node.js 依存関係を確認

```bash
cd ~/agenticseek

# npm 依存関係を確認
npm list | head -20

# 必要に応じて再インストール
npm install
```

---

### Phase 3: 起動スクリプトの修正と テスト

#### タスク 3.1: バックエンド API を起動テスト

**ターミナル 1:**
```bash
cd ~/agenticseek
source venv/bin/activate

# 環境変数を設定
export DEEPSEEK_API_KEY="sk-d8d78811ea69434fad5d447b5c1027e3"
export PORT=7777

# API サーバーを起動
python server/api.py
```

**期待される出力:**
```
INFO:     Uvicorn running on http://127.0.0.1:7777 (Press CTRL+C to quit)
```

**テスト:**
別のターミナルで以下を実行：
```bash
curl http://localhost:7777/
```

**期待される出力:**
```json
{"name": "AgenticSeek API", "version": "1.0.0"}
```

---

#### タスク 3.2: フロントエンドを起動テスト

**ターミナル 2:**
```bash
cd ~/agenticseek

# 環境変数を設定
export VITE_API_BASE_URL="http://localhost:7777"

# フロントエンドを起動
npm run dev
```

**期待される出力:**
```
VITE v5.4.21 ready in 114 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

---

#### タスク 3.3: ブラウザでテスト

```
http://localhost:5173
```

**確認事項:**
- [ ] AgenticSeek ロゴが表示される
- [ ] 6 つのタブが表示される（Agent、Browser、Files、Code、GitHub、Deploy）
- [ ] Agent タブにテキストエリアが表示される
- [ ] 実行ボタンが表示される
- [ ] コンソールにエラーがない

---

### Phase 4: 統合起動スクリプトの修正

#### タスク 4.1: start-dev.sh を修正

**問題点:**
- 現在の `start-dev.sh` が Mac で正常に動作していない
- バックグラウンド起動に問題がある

**修正内容:**

```bash
# ~/agenticseek/start-dev.sh を以下に置き換え
```

```bash
#!/bin/bash

# AgenticSeek Development Environment Startup Script for macOS
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}🚀 AgenticSeek Development Environment${NC}"
echo ""

# Check for required tools
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

# Create Python virtual environment if needed
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Install Python dependencies
echo -e "${YELLOW}📥 Installing Python dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$SCRIPT_DIR/server/requirements.txt" > /dev/null 2>&1

# Install Playwright
echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
playwright install chromium > /dev/null 2>&1

# Set environment variables
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-sk-d8d78811ea69434fad5d447b5c1027e3}"
export VITE_API_BASE_URL="http://localhost:7777"
export PORT=7777

echo -e "${BLUE}🔧 Starting services...${NC}"
echo ""

# Start backend in background
echo -e "${YELLOW}📍 Starting Backend API Server on port 7777...${NC}"
python "$SCRIPT_DIR/server/api.py" &
BACKEND_PID=$!
sleep 2

# Start frontend in background
echo -e "${YELLOW}📍 Starting Frontend Development Server on port 5173...${NC}"
npm run dev &
FRONTEND_PID=$!
sleep 2

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ AgenticSeek is Ready!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}🌐 Frontend: http://localhost:5173${NC}"
echo -e "${YELLOW}🔧 Backend API: http://localhost:7777${NC}"
echo -e "${YELLOW}📚 API Docs: http://localhost:7777/docs${NC}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Stopped${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# Wait for processes
wait
```

**実施:**
```bash
# ファイルを置き換え
nano ~/agenticseek/start-dev.sh
# または
cat > ~/agenticseek/start-dev.sh << 'EOF'
[上記のスクリプト内容]
EOF

# パーミッション設定
chmod +x ~/agenticseek/start-dev.sh
```

---

#### タスク 4.2: start-dev.sh をテスト

```bash
cd ~/agenticseek
./start-dev.sh
```

**期待される出力:**
```
✅ AgenticSeek is Ready!
🌐 Frontend: http://localhost:5173
🔧 Backend API: http://localhost:7777
```

---

### Phase 5: ワンクリック起動の設定

#### タスク 5.1: AgenticSeekLauncher.command を修正

```bash
cat > ~/agenticseek/AgenticSeekLauncher.command << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
chmod +x start-dev.sh
./start-dev.sh
EOF

chmod +x ~/agenticseek/AgenticSeekLauncher.command
```

---

#### タスク 5.2: Dock に追加

1. Finder で `~/agenticseek/AgenticSeekLauncher.command` を探す
2. Dock にドラッグ
3. 次回から Dock をクリックで起動

---

### Phase 6: 機能テスト

#### タスク 6.1: 各タブの機能をテスト

```
Agent タブ:
- テキストエリアに「Google にアクセスしてスクリーンショットを取得」と入力
- 実行ボタンをクリック
- 結果が表示されることを確認

Browser タブ:
- URL を入力
- アクセスボタンをクリック
- スクリーンショットが表示されることを確認

Code タブ:
- Python コードを入力
- 実行ボタンをクリック
- 出力が表示されることを確認

Files タブ:
- ファイルパスを入力
- 読み込みボタンをクリック
- ファイル内容が表示されることを確認

GitHub タブ:
- GitHub 操作をテスト

Deploy タブ:
- デプロイ情報を確認
```

---

### Phase 7: 本番環境デプロイ（オプション）

#### タスク 7.1: バックエンド API を Railway にデプロイ

1. Railway アカウントを作成
2. `server/` をデプロイ
3. 環境変数を設定
4. デプロイ URL を確認

---

#### タスク 7.2: フロントエンドを Netlify にデプロイ

1. Netlify にログイン
2. GitHub リポジトリを接続
3. ビルド設定を確認
4. デプロイ

---

## ✅ チェックリスト

### Phase 1
- [ ] server/ ディレクトリが作成されている
- [ ] api.py がコピーされている
- [ ] requirements.txt がコピーされている
- [ ] GitHub にプッシュされている

### Phase 2
- [ ] Python 依存関係がインストールされている
- [ ] Playwright がインストールされている
- [ ] npm 依存関係が確認されている

### Phase 3
- [ ] バックエンド API が起動する
- [ ] フロントエンドが起動する
- [ ] ブラウザでアクセスできる
- [ ] 6 つのタブが表示される

### Phase 4
- [ ] start-dev.sh が修正されている
- [ ] start-dev.sh でワンクリック起動できる

### Phase 5
- [ ] AgenticSeekLauncher.command が実行可能
- [ ] Dock に追加できる

### Phase 6
- [ ] 各タブの機能がテストされている

### Phase 7
- [ ] バックエンド API が本番環境にデプロイされている
- [ ] フロントエンドが本番環境にデプロイされている

---

## 🔗 参考ドキュメント

- `CLAUDE_HANDOFF.md` - 完全な引き継ぎドキュメント
- `CLAUDE_FIRST_STEPS.md` - 最初のステップ
- `LOCAL_SETUP.md` - ローカルセットアップガイド
- `NETLIFY_DEPLOYMENT.md` - Netlify デプロイガイド
- `PROJECT_SUMMARY.md` - プロジェクト総括

---

## 📞 トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'fastapi'`

```bash
source venv/bin/activate
pip install -r server/requirements.txt
```

### エラー: `playwright: command not found`

```bash
pip install playwright
playwright install chromium
```

### エラー: ポートが既に使用されている

```bash
# ポート 7777 を確認
lsof -i :7777

# ポート 5173 を確認
lsof -i :5173

# プロセスを終了
kill -9 <PID>
```

---

**Claude Code で上記のタスクを順序通り実施してください！** 🚀
