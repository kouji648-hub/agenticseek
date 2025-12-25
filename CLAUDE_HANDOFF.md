# AgenticSeek - Claude Code への引き継ぎドキュメント

## 📋 プロジェクト概要

**プロジェクト名**: AgenticSeek
**説明**: 自立型 AI エージェント - 自然言語で自動化タスク実行
**状態**: フロントエンド完成、バックエンド API 実装済み、Mac 統合中

---

## 🎯 現在の状況

### ✅ 完了した項目

1. **フロントエンド（React + Tailwind CSS）**
   - 6 つのタブ UI 完成（Agent、Browser、Files、Code、GitHub、Deploy）
   - Manus で実装済み
   - URL: https://agenticseek-pibmxpgd.manus.space/

2. **バックエンド API（FastAPI）**
   - `server/api.py` 実装済み（1000+ 行）
   - エンドポイント実装済み：
     - `/agent` - AI エージェント実行
     - `/browse` - ブラウザ自動化
     - `/execute/python` - Python 実行
     - `/execute/javascript` - JavaScript 実行
     - `/files` - ファイル操作
     - `/github` - GitHub 統合
     - `/upload` - ファイルアップロード

3. **ドキュメント**
   - `LOCAL_SETUP.md` - ローカルセットアップガイド
   - `NETLIFY_DEPLOYMENT.md` - Netlify デプロイガイド
   - `PROJECT_SUMMARY.md` - プロジェクト総括
   - `QUICK_START.md` - クイックスタート
   - `MAC_RESTART_GUIDE.md` - Mac 再起動ガイド

### ⚠️ 進行中の問題

1. **Mac ローカル環境の統合**
   - `~/agenticseek` に `server/` ディレクトリがない
   - `api.py` と `requirements.txt` を Mac にコピーが必要
   - GitHub リポジトリに `server/` がプッシュされていない

2. **起動スクリプトの問題**
   - `start-dev.sh` は作成されたが、実行に問題がある
   - バックエンド API が起動していない

---

## 📁 ファイル構成

### Manus プロジェクト（`/home/ubuntu/agenticseek-frontend`）

```
/home/ubuntu/agenticseek-frontend/
├── client/                          # React フロントエンド
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx            # メイン UI（6 タブ）
│   │   │   └── NotFound.tsx
│   │   ├── components/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   └── public/
├── server/                          # FastAPI バックエンド
│   ├── api.py                      # メイン API サーバー
│   ├── requirements.txt            # Python 依存関係
│   ├── start.sh                    # バックエンド起動スクリプト
│   └── README.md
├── netlify/
│   └── functions/
│       └── agent.ts                # Netlify Functions
├── vite.config.ts
├── netlify.toml
├── start-dev.sh                    # 統合起動スクリプト
├── AgenticSeekLauncher.command     # Mac ランチャー
├── package.json
├── tsconfig.json
├── LOCAL_SETUP.md
├── NETLIFY_DEPLOYMENT.md
├── PROJECT_SUMMARY.md
├── QUICK_START.md
├── MAC_RESTART_GUIDE.md
└── CLAUDE_HANDOFF.md              # このファイル
```

### Mac ローカル（`~/agenticseek`）

```
~/agenticseek/
├── frontend/                        # フロントエンド（古い）
├── src/                             # フロントエンド
├── venv/                            # Python 仮想環境
├── node_modules/
├── package.json
├── vite.config.js
├── start-dev.sh                     # 作成済み
└── (server/ がない ❌)
```

---

## 🔧 必要な作業

### 優先度 1: Mac ローカル環境の完成

**タスク:**

1. **server/ ディレクトリを Mac にコピー**
   ```bash
   mkdir -p ~/agenticseek/server
   # Manus から以下をコピー:
   # - /home/ubuntu/agenticseek-frontend/server/api.py
   # - /home/ubuntu/agenticseek-frontend/server/requirements.txt
   ```

2. **GitHub にプッシュ**
   ```bash
   cd ~/agenticseek
   git add server/
   git commit -m "Add backend API server"
   git push origin main
   ```

3. **Mac で起動テスト**
   ```bash
   cd ~/agenticseek
   source venv/bin/activate
   pip install -r server/requirements.txt
   python server/api.py
   ```

4. **フロントエンド＆バックエンド統合テスト**
   - ターミナル 1: `npm run dev`
   - ターミナル 2: `python server/api.py`
   - ブラウザ: http://localhost:5173

### 優先度 2: ワンクリック起動の実装

**タスク:**

1. `start-dev.sh` を修正（Mac 対応）
2. `AgenticSeekLauncher.command` を Mac で実行可能にする
3. Dock に追加できるようにする

### 優先度 3: 本番環境デプロイ

**タスク:**

1. バックエンド API を Railway/Render/AWS Lambda にデプロイ
2. Netlify にフロントエンドをデプロイ
3. 環境変数を設定（`VITE_API_BASE_URL`）
4. 本番環境でテスト

---

## 📊 技術スタック

### フロントエンド
- React 19
- Vite 7.1.9
- TypeScript 5.6
- Tailwind CSS 4
- shadcn/ui
- Wouter (ルーティング)

### バックエンド
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Playwright 1.40.0
- Python 3.8+

### 外部サービス
- DeepSeek API (LLM)
- Claude API (オプション)
- GitHub API
- Netlify (ホスティング)

---

## 🚀 起動手順

### ローカル開発（Mac）

**方法 1: 統合スクリプト**
```bash
cd ~/agenticseek
./start-dev.sh
```

**方法 2: 手動起動**

ターミナル 1:
```bash
cd ~/agenticseek
npm run dev
```

ターミナル 2:
```bash
cd ~/agenticseek
source venv/bin/activate
python server/api.py
```

**ブラウザ:**
```
http://localhost:5173  # フロントエンド
http://localhost:7777  # バックエンド API
http://localhost:7777/docs  # API ドキュメント
```

---

## 🔑 環境変数

### Mac ローカル

```bash
# .env または環境変数として設定
DEEPSEEK_API_KEY=sk-d8d78811ea69434fad5d447b5c1027e3
VITE_API_BASE_URL=http://localhost:7777
PORT=7777
```

### 本番環境（Netlify）

```
VITE_API_BASE_URL=https://api.agenticseek.com
```

---

## 📝 API エンドポイント

### AI エージェント
```
POST /agent
{
  "prompt": "Google にアクセスしてスクリーンショットを取得",
  "max_steps": 10
}
```

### ブラウザ自動化
```
POST /browse
{
  "url": "https://www.google.com",
  "action": "screenshot"
}
```

### Python 実行
```
POST /execute/python
{
  "code": "print('Hello World')"
}
```

### ファイル操作
```
POST /files
{
  "action": "read",
  "path": "/path/to/file"
}
```

---

## 🧪 テスト項目

- [ ] フロントエンド起動確認
- [ ] バックエンド API 起動確認
- [ ] Agent タブ動作確認
- [ ] Browser タブ動作確認
- [ ] Code タブ動作確認
- [ ] Files タブ動作確認
- [ ] GitHub タブ動作確認
- [ ] Deploy タブ動作確認
- [ ] Netlify デプロイ確認
- [ ] 本番環境動作確認

---

## 📞 次のステップ

1. **Mac ローカル環境を完成させる**
   - server/ をコピー
   - GitHub にプッシュ
   - 起動テスト

2. **ワンクリック起動を実装**
   - start-dev.sh を修正
   - Dock に追加

3. **本番環境にデプロイ**
   - バックエンド API をデプロイ
   - Netlify にデプロイ
   - 環境変数を設定

4. **ユーザー認証を追加**
   - Manus OAuth 統合
   - ユーザー管理

5. **データベース統合**
   - 実行履歴保存
   - ユーザーデータ管理

---

## 🔗 リンク

- **GitHub**: https://github.com/kouji648-hub/agenticseek
- **Manus Frontend**: https://agenticseek-pibmxpgd.manus.space/
- **Netlify**: https://app.netlify.com

---

## 📌 重要な注意事項

1. **server/ ディレクトリが Mac にない**
   - Manus から Mac にコピーが必要
   - GitHub にプッシュが必要

2. **環境変数の設定**
   - `DEEPSEEK_API_KEY` を設定
   - `VITE_API_BASE_URL` を設定

3. **Playwright のインストール**
   - `playwright install chromium` が必要

4. **Python 仮想環境**
   - `venv/` が既に作成されている
   - `source venv/bin/activate` で有効化

---

**Claude Code での作業を開始してください！** 🚀
