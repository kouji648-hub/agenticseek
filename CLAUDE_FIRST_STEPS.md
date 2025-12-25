# Claude Code - 最初のステップ

## 🎯 今すぐやること（5 分で完了）

### ステップ 1: Mac のターミナルで server/ をコピー

```bash
# Mac のターミナルで実行
cd ~/agenticseek

# server ディレクトリを作成
mkdir -p server

# 以下のファイルを Manus からダウンロードして保存
# - server/api.py
# - server/requirements.txt
# - server/README.md
# - server/start.sh
```

**または、Manus から直接ダウンロード：**

Manus の Management UI → **Code** パネルで以下をダウンロード：
- `server/api.py`
- `server/requirements.txt`
- `server/start.sh`
- `server/README.md`

ダウンロード後、`~/agenticseek/server/` に保存してください。

---

### ステップ 2: GitHub にプッシュ

```bash
cd ~/agenticseek

# ファイルを追加
git add server/
git add *.md

# コミット
git commit -m "Add backend API server and documentation"

# プッシュ
git push origin main
```

---

### ステップ 3: バックエンド API を起動テスト

**ターミナル 1:**
```bash
cd ~/agenticseek
source venv/bin/activate
pip install -r server/requirements.txt
python server/api.py
```

**期待される出力：**
```
INFO:     Uvicorn running on http://127.0.0.1:7777
```

---

### ステップ 4: フロントエンドが起動しているか確認

**ターミナル 2:**
```bash
cd ~/agenticseek
npm run dev
```

**期待される出力：**
```
VITE v5.4.21 ready in 114 ms
Local: http://localhost:5173/
```

---

### ステップ 5: ブラウザでテスト

ブラウザで以下にアクセス：

```
http://localhost:5173
```

**確認事項：**
- ✅ AgenticSeek ロゴが表示される
- ✅ 6 つのタブが表示される（Agent、Browser、Files、Code、GitHub、Deploy）
- ✅ Agent タブにテキストエリアが表示される
- ✅ 実行ボタンが表示される

---

## 🔧 トラブルシューティング

### エラー 1: `ModuleNotFoundError: No module named 'fastapi'`

```bash
cd ~/agenticseek
source venv/bin/activate
pip install -r server/requirements.txt
```

### エラー 2: `playwright: command not found`

```bash
pip install playwright
playwright install chromium
```

### エラー 3: ポートが既に使用されている

```bash
# ポート 7777 を確認
lsof -i :7777

# ポート 5173 を確認
lsof -i :5173

# プロセスを終了
kill -9 <PID>
```

### エラー 4: `npm: command not found`

```bash
# Node.js をインストール
brew install node
```

---

## 📋 チェックリスト

- [ ] server/ ディレクトリを作成
- [ ] api.py をコピー
- [ ] requirements.txt をコピー
- [ ] GitHub にプッシュ
- [ ] バックエンド API を起動
- [ ] フロントエンドを起動
- [ ] ブラウザでテスト
- [ ] 6 つのタブが表示されることを確認

---

## ✅ 完了後の次のステップ

1. **ワンクリック起動スクリプトを修正**
   - `start-dev.sh` を Mac 対応に修正
   - テスト実行

2. **各タブの機能をテスト**
   - Agent タブ: AI エージェント実行
   - Browser タブ: ブラウザ自動化
   - Code タブ: Python/JavaScript 実行
   - Files タブ: ファイル操作
   - GitHub タブ: GitHub 統合
   - Deploy タブ: デプロイメント

3. **本番環境にデプロイ**
   - バックエンド API を Railway/Render にデプロイ
   - Netlify にフロントエンドをデプロイ

---

## 📞 質問がある場合

- `CLAUDE_HANDOFF.md` - 完全な引き継ぎドキュメント
- `LOCAL_SETUP.md` - ローカルセットアップガイド
- `PROJECT_SUMMARY.md` - プロジェクト総括

---

**これで準備完了です！** 🚀

次は Claude Code で以下を実行してください：

1. Mac のターミナルで server/ をコピー
2. GitHub にプッシュ
3. バックエンド API を起動
4. ブラウザでテスト
