# AgenticSeek - クイックスタートガイド

このガイドでは、AgenticSeek をすぐに始める方法を説明します。

## 🚀 5 分で始める

### ステップ 1: リポジトリをクローン

```bash
git clone https://github.com/kouji648-hub/agenticseek.git
cd agenticseek
```

### ステップ 2: 依存関係をインストール

```bash
# Node.js 依存関係
npm install

# Python 依存関係（初回のみ）
python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
playwright install chromium
```

### ステップ 3: 開発環境を起動

#### macOS/Linux

```bash
chmod +x start-dev.sh
./start-dev.sh
```

#### Windows

```bash
# ターミナル 1: バックエンド
python server/api.py

# ターミナル 2: フロントエンド
npm run dev
```

### ステップ 4: ブラウザでアクセス

- **フロントエンド**: http://localhost:3000
- **バックエンド API**: http://localhost:7777
- **API ドキュメント**: http://localhost:7777/docs

## 📝 使用例

### AI エージェントを実行

1. フロントエンドで **"Agent"** タブをクリック
2. テキストボックスに以下を入力：
   ```
   Google にアクセスして、スクリーンショットを取得してください
   ```
3. **"実行"** ボタンをクリック

### Python コードを実行

1. **"Code"** タブをクリック
2. Python コードを入力：
   ```python
   print("Hello AgenticSeek!")
   ```
3. **"実行"** ボタンをクリック

### ブラウザを自動化

1. **"Browser"** タブをクリック
2. URL を入力：
   ```
   https://www.google.com
   ```
3. **"アクセス"** ボタンをクリック

## 🔧 トラブルシューティング

### ポートが既に使用されている場合

自動起動スクリプトは自動的に別のポートを探します。

### Playwright のインストール失敗

```bash
playwright install chromium
```

### Python モジュールが見つからない

```bash
source venv/bin/activate
pip install -r server/requirements.txt
```

## 📚 詳細ドキュメント

- **ローカルセットアップ**: `LOCAL_SETUP.md`
- **Netlify デプロイ**: `NETLIFY_DEPLOYMENT.md`
- **プロジェクト概要**: `PROJECT_SUMMARY.md`
- **バックエンド API**: `server/README.md`

## 🌐 本番環境へのデプロイ

### Netlify へのデプロイ

```bash
npm run build
netlify deploy --prod
```

### バックエンド API のデプロイ

Railway、Render、AWS Lambda などのプラットフォームに `server/api.py` をデプロイしてください。

## 🆘 サポート

問題が発生した場合：

1. `LOCAL_SETUP.md` のトラブルシューティングを確認
2. ログファイルを確認：
   ```bash
   tail -f /tmp/agenticseek-logs/frontend.log
   tail -f /tmp/agenticseek-logs/backend.log
   ```
3. GitHub Issues で報告

## 📞 次のステップ

- [ ] ローカルで起動してテスト
- [ ] バックエンド API をカスタマイズ
- [ ] 本番環境にデプロイ
- [ ] ユーザー認証を追加
- [ ] データベース統合

---

**Happy Coding! 🚀**
