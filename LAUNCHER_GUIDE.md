# AgenticSeek 1クリック起動ガイド

## 🚀 デスクトップランチャー

AgenticSeek を1クリックで起動できるランチャーをデスクトップに配置しました！

---

## 📍 ファイル場所

**デスクトップ:** `~/Desktop/AgenticSeek起動.command`

---

## 🎯 使い方

### 起動方法

1. **デスクトップの「AgenticSeek起動.command」をダブルクリック**
2. ターミナルウィンドウが開き、起動プロセスが表示されます
3. 自動的にブラウザが開きます
4. AgenticSeek が利用可能になります！

### 起動時に何が起こるか

ランチャーは以下を自動的に実行します：

1. ✅ 既存のプロセスを停止（クリーンスタート）
2. ✅ バックエンドAPI起動（Python + FastAPI）
3. ✅ フロントエンド起動（React + Vite）
4. ✅ サービスの起動確認
5. ✅ ブラウザを自動的に開く

### 表示される情報

```
🚀 AgenticSeek を起動中...
================================
📁 プロジェクトディレクトリ: /Users/kawabatakouji/agenticseek

🛑 既存のプロセスを停止中...
🔧 バックエンドAPIを起動中...
   ✓ バックエンドPID: xxxxx
🎨 フロントエンドを起動中...
   ✓ フロントエンドPID: xxxxx

⏳ サービスの起動を確認中...
   ✅ バックエンドAPI: 起動成功 (http://localhost:7777)
   ✅ フロントエンド: 起動成功 (http://localhost:3001)

================================
✨ AgenticSeek が起動しました！
================================

📍 アクセスURL:
   🌐 フロントエンド: http://localhost:3001
   🔧 バックエンドAPI: http://localhost:7777
   📚 API ドキュメント: http://localhost:7777/docs
```

---

## 🛑 停止方法

### 方法1: ターミナルから停止
- ターミナルウィンドウで **Ctrl + C** を押す

### 方法2: ウィンドウを閉じる
- ターミナルウィンドウを閉じる
- プロセスは自動的に停止します

---

## 📊 アクセスURL

起動後、以下のURLでアクセスできます：

| サービス | URL | 説明 |
|---------|-----|------|
| **フロントエンド** | http://localhost:3001 | メインUI（7タブ） |
| **バックエンドAPI** | http://localhost:7777 | REST API |
| **APIドキュメント** | http://localhost:7777/docs | Swagger UI |
| **ヘルスチェック** | http://localhost:7777/health | 稼働状態確認 |

---

## 📝 ログファイル

トラブルシューティング用のログファイル：

| ログ | 場所 |
|------|------|
| **バックエンド** | `/tmp/agenticseek-backend.log` |
| **フロントエンド** | `/tmp/agenticseek-frontend.log` |

### ログの確認方法

```bash
# バックエンドログ
tail -f /tmp/agenticseek-backend.log

# フロントエンドログ
tail -f /tmp/agenticseek-frontend.log
```

---

## 🎨 利用可能な機能

起動後、ブラウザで以下のタブにアクセスできます：

1. **🤖 Agent** - AI エージェント実行
2. **💬 Chat** - チャット機能（追跡質問付き）
3. **🌐 Browser** - ブラウザ自動化
4. **📁 Files** - ファイル操作
5. **⚙️ Code** - Python/JavaScript 実行
6. **🔗 GitHub** - GitHub 統合
7. **🚀 Deploy** - デプロイ機能

---

## 🔧 トラブルシューティング

### 起動しない場合

1. **ターミナルのエラーメッセージを確認**
   - ランチャーを実行すると詳細なエラーが表示されます

2. **手動で起動を試す**
   ```bash
   cd ~/agenticseek
   source venv/bin/activate
   python server/api.py
   ```

3. **依存関係を再インストール**
   ```bash
   cd ~/agenticseek
   source venv/bin/activate
   pip install -r server/requirements.txt
   npm install
   ```

### ポートが使用中の場合

既存のプロセスを手動で停止：

```bash
# プロセスを確認
lsof -i :7777
lsof -i :3001

# プロセスを停止
pkill -f "python.*server/api.py"
pkill -f "vite.*--host"
```

### ブラウザが開かない場合

手動でブラウザを開く：
```
http://localhost:3001
```

---

## 📱 スマホでアクセス

同じWi-Fiに接続していれば、スマホからもアクセス可能：

1. MacのIPアドレスを確認
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. スマホのブラウザで以下のようなURLを開く
   ```
   http://192.168.x.x:3001/
   ```

---

## 🎯 便利な使い方

### Dockに追加

1. デスクトップの「AgenticSeek起動.command」を
2. Dockの右側（アプリケーション領域）にドラッグ＆ドロップ

### エイリアスを作成

他の場所からも起動できるようにエイリアスを作成：

1. Finder でファイルを右クリック
2. 「エイリアスを作成」を選択
3. 好きな場所に配置

---

## 🔄 自動起動設定（オプション）

Mac起動時に自動起動させたい場合：

1. **システム設定** を開く
2. **一般** → **ログイン項目**
3. 「+」ボタンをクリック
4. 「AgenticSeek起動.command」を選択

---

## 📚 関連ドキュメント

- **プロジェクト概要**: `CLAUDE_HANDOFF.md`
- **チャット機能**: `CHAT_FEATURE_DOCUMENTATION.md`
- **Railway デプロイ**: `RAILWAY_DEPLOYMENT_GUIDE.md`
- **ローカルセットアップ**: `LOCAL_SETUP.md`

---

## 🆘 サポート

問題が発生した場合：

1. **GitHub Issues**: https://github.com/kouji648-hub/agenticseek/issues
2. **ログファイルを確認**: `/tmp/agenticseek-*.log`
3. **手動起動を試す**: `cd ~/agenticseek && ./AgenticSeek起動.command`

---

**デスクトップから1クリックで AgenticSeek を楽しんでください！** 🚀✨
