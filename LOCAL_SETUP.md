# AgenticSeek - ローカル開発環境セットアップガイド

このガイドでは、Mac ローカルマシンで AgenticSeek を実行するための手順を説明します。

## 前提条件

- **macOS 10.15 以上**
- **Node.js 16 以上** ([nodejs.org](https://nodejs.org/) からインストール)
- **Python 3.8 以上** (通常は macOS に付属)
- **npm または pnpm** (Node.js に含まれる)

## インストール手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/kouji648-hub/agenticseek.git
cd agenticseek
```

### 2. フロントエンド依存関係をインストール

```bash
npm install
# または
pnpm install
```

### 3. バックエンド依存関係をインストール（初回のみ）

```bash
# Python 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存関係をインストール
pip install -r server/requirements.txt

# Playwright ブラウザをインストール
playwright install chromium
```

## 実行方法

### 方法 1: 自動起動スクリプト（推奨）

#### macOS（ターミナル）

```bash
chmod +x start-dev.sh
./start-dev.sh
```

または、Finder から `AgenticSeekLauncher.command` をダブルクリック

#### 出力例

```
🚀 AgenticSeek Development Environment
========================================

✅ Frontend port: 3000
✅ Backend port: 7777

✅ Backend API Server started (PID: 12345)
   📍 URL: http://localhost:7777

✅ Frontend Development Server started (PID: 12346)
   📍 URL: http://localhost:3000

========================================
✅ AgenticSeek Development Environment Ready!
========================================

Frontend:
  🌐 URL: http://localhost:3000
  📝 Logs: /tmp/agenticseek-logs/frontend.log

Backend API:
  🌐 URL: http://localhost:7777
  📚 Docs: http://localhost:7777/docs
  📝 Logs: /tmp/agenticseek-logs/backend.log
```

### 方法 2: 手動で起動

#### ターミナル 1: バックエンド API

```bash
# Python 仮想環境を有効化
source venv/bin/activate

# バックエンド API を起動
python server/api.py
```

#### ターミナル 2: フロントエンド

```bash
# フロントエンド開発サーバーを起動
npm run dev
# または
pnpm dev
```

## アクセス

- **フロントエンド**: http://localhost:3000
- **バックエンド API**: http://localhost:7777
- **API ドキュメント**: http://localhost:7777/docs

## 環境変数の設定

### バックエンド環境変数

`.env` ファイルを作成して、以下の変数を設定します：

```bash
# DeepSeek API Key（必須）
DEEPSEEK_API_KEY=sk-d8d78811ea69434fad5d447b5c1027e3

# Claude API Key（オプション）
ANTHROPIC_API_KEY=your-claude-api-key

# GitHub Personal Access Token（オプション）
GITHUB_TOKEN=your-github-token

# サーバーポート（デフォルト: 7777）
PORT=7777
```

### フロントエンド環境変数

`.env.local` ファイルを作成して、以下の変数を設定します：

```bash
# バックエンド API の URL
VITE_API_BASE_URL=http://localhost:7777
```

## トラブルシューティング

### ポートが既に使用されている場合

自動起動スクリプトは自動的に別のポートを探します。

手動で起動する場合は、以下のコマンドで別のポートを指定します：

```bash
# フロントエンド（ポート 3001 を使用）
npm run dev -- --port 3001

# バックエンド（ポート 7778 を使用）
PORT=7778 python server/api.py
```

### Playwright のインストール失敗

```bash
# Playwright ブラウザを再インストール
playwright install chromium

# または、システム依存関係をインストール（Linux/Ubuntu の場合）
sudo apt-get install -y libgconf-2-4 libatk1.0-0 libatk-bridge2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb
```

### Python 仮想環境の問題

```bash
# 仮想環境を削除して再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

### Node.js モジュールの問題

```bash
# node_modules を削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

## プロセスの停止

### 自動起動スクリプトの場合

- `Ctrl+C` を押してスクリプトを停止
- または、ターミナルを閉じる

### 手動で起動した場合

各ターミナルで `Ctrl+C` を押す

### プロセスを強制終了する場合

```bash
# ポート 3000 を使用しているプロセスを終了
lsof -ti:3000 | xargs kill -9

# ポート 7777 を使用しているプロセスを終了
lsof -ti:7777 | xargs kill -9
```

## 開発ワークフロー

### フロントエンドの開発

1. `client/src/pages/Home.tsx` でコンポーネントを編集
2. ブラウザが自動的にリロード（Hot Module Replacement）
3. 変更を確認

### バックエンドの開発

1. `server/api.py` を編集
2. バックエンド API を再起動（`Ctrl+C` → `python server/api.py`）
3. API ドキュメント（http://localhost:7777/docs）で変更を確認

## デバッグ

### ログの確認

```bash
# フロントエンドログ
tail -f /tmp/agenticseek-logs/frontend.log

# バックエンドログ
tail -f /tmp/agenticseek-logs/backend.log
```

### ブラウザ開発者ツール

- Chrome/Safari: `F12` または `Cmd+Option+I`
- ネットワークタブで API リクエストを確認

### API テスト

```bash
# ヘルスチェック
curl http://localhost:7777/health

# Python コード実行
curl -X POST http://localhost:7777/execute/python \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")"}'
```

## 本番環境へのデプロイ

### Netlify へのデプロイ

```bash
# フロントエンドをビルド
npm run build

# Netlify CLI でデプロイ
npm install -g netlify-cli
netlify deploy --prod --dir=dist/public
```

### バックエンド API のデプロイ

バックエンド API は以下のプラットフォームにデプロイできます：

- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://www.heroku.com
- **AWS Lambda**: https://aws.amazon.com/lambda/
- **Google Cloud Run**: https://cloud.google.com/run

## 次のステップ

1. フロントエンドで各タブの機能をテスト
2. バックエンド API のエンドポイントをテスト
3. 必要に応じて機能を追加
4. 本番環境にデプロイ

## サポート

問題が発生した場合は、以下をご確認ください：

1. すべての前提条件がインストールされているか
2. ポートが使用可能か
3. API キーが正しく設定されているか
4. ログファイルでエラーメッセージを確認

## ライセンス

MIT

---

**Happy Coding! 🚀**
