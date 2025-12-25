# Mac 再起動後の AgenticSeek 起動ガイド

Mac を再起動した後、AgenticSeek を起動する方法を説明します。

## 方法 1: Finder から起動（最も簡単）⭐ 推奨

### ステップ 1: Finder を開く

- **Cmd + Space** キーを押す
- "Finder" と入力して Enter

### ステップ 2: プロジェクトフォルダに移動

```
ホーム > agenticseek
```

または、Finder で以下のパスに移動：

```
~/agenticseek
```

### ステップ 3: ランチャーをダブルクリック

`AgenticSeekLauncher.command` ファイルをダブルクリック

**初回のみ：**

1. セキュリティ警告が表示される場合があります
2. **"開く"** をクリック
3. ターミナルが開き、自動的に起動します

### ステップ 4: ブラウザでアクセス

ターミナルに表示される URL をクリック：

```
🌐 URL: http://localhost:3000
```

---

## 方法 2: ターミナルから起動

### ステップ 1: ターミナルを開く

- **Cmd + Space** キーを押す
- "ターミナル" と入力して Enter

### ステップ 2: プロジェクトディレクトリに移動

```bash
cd ~/agenticseek
```

### ステップ 3: 起動スクリプトを実行

```bash
chmod +x start-dev.sh
./start-dev.sh
```

### ステップ 4: ブラウザでアクセス

出力されたログから URL をコピー：

```
🌐 URL: http://localhost:3000
```

---

## 方法 3: VS Code から起動

### ステップ 1: VS Code を開く

- **Cmd + Space** キーを押す
- "VS Code" と入力して Enter

### ステップ 2: フォルダを開く

- **Cmd + O** キーを押す
- `~/agenticseek` を選択

### ステップ 3: ターミナルを開く

- **Ctrl + `** キーを押す（またはメニューから Terminal → New Terminal）

### ステップ 4: 起動スクリプトを実行

```bash
chmod +x start-dev.sh
./start-dev.sh
```

---

## 方法 4: Automator で自動起動（上級）

### ステップ 1: Automator を開く

- **Cmd + Space** キーを押す
- "Automator" と入力して Enter

### ステップ 2: 新規ドキュメントを作成

- **File** → **New**
- **Application** を選択

### ステップ 3: スクリプトを追加

左側のライブラリから **"Run Shell Script"** をドラッグ

以下のスクリプトを入力：

```bash
cd ~/agenticseek
chmod +x start-dev.sh
./start-dev.sh
```

### ステップ 4: 保存

- **File** → **Save**
- 名前: `AgenticSeek Launcher`
- 場所: **Applications**

### ステップ 5: 起動

Applications フォルダから `AgenticSeek Launcher` をダブルクリック

---

## トラブルシューティング

### ターミナルが開かない場合

1. セキュリティ設定を確認：
   - **System Preferences** → **Security & Privacy**
   - **General** タブで許可を確認

2. ファイルのパーミッションを確認：
   ```bash
   chmod +x ~/agenticseek/start-dev.sh
   chmod +x ~/agenticseek/AgenticSeekLauncher.command
   ```

### ポートが既に使用されている場合

自動起動スクリプトは自動的に別のポートを探します。

ターミナルの出力から実際のポート番号を確認してください：

```
✅ Frontend port: 3001  # または別のポート
✅ Backend port: 7778   # または別のポート
```

### Python 仮想環境エラー

```bash
cd ~/agenticseek
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r server/requirements.txt
```

### Node.js モジュールエラー

```bash
cd ~/agenticseek
rm -rf node_modules package-lock.json
npm install
```

---

## 起動後の確認

### ✅ 正常に起動している場合

ターミナルに以下のように表示されます：

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
```

### ✅ ブラウザでアクセス

以下の URL にアクセス：

- **フロントエンド**: http://localhost:3000
- **バックエンド API**: http://localhost:7777
- **API ドキュメント**: http://localhost:7777/docs

---

## 停止方法

### ターミナルから停止

ターミナルで **Ctrl + C** を押す

### プロセスを強制終了

別のターミナルで以下を実行：

```bash
# ポート 3000 を停止
lsof -ti:3000 | xargs kill -9

# ポート 7777 を停止
lsof -ti:7777 | xargs kill -9
```

---

## 推奨される起動方法

| 方法 | 難易度 | 推奨度 |
|------|------|------|
| Finder から起動 | ⭐ 簡単 | ⭐⭐⭐⭐⭐ |
| ターミナルから起動 | ⭐⭐ 中程度 | ⭐⭐⭐⭐ |
| VS Code から起動 | ⭐⭐⭐ やや難 | ⭐⭐⭐ |
| Automator で自動起動 | ⭐⭐⭐⭐ 難 | ⭐⭐ |

**初心者向け**: 方法 1（Finder から起動）
**開発者向け**: 方法 2（ターミナルから起動）

---

## よくある質問

**Q: 毎回ターミナルを開くのは面倒です**

A: Finder から `AgenticSeekLauncher.command` をダブルクリックするだけで起動できます。

**Q: バックグラウンドで実行できますか？**

A: はい。ターミナルウィンドウを最小化すれば、バックグラウンドで実行されます。

**Q: 自動的に起動することはできますか？**

A: はい。ログイン時に自動起動するように設定できます（Automator を使用）。

**Q: 複数のプロジェクトを同時に実行できますか？**

A: はい。別のターミナルウィンドウで異なるポートを指定して実行できます。

---

## 次のステップ

1. ✅ Mac を再起動
2. ✅ AgenticSeek を起動
3. ✅ ブラウザで http://localhost:3000 にアクセス
4. ✅ 各タブの機能をテスト
5. ✅ Netlify にデプロイ

---

**Happy Coding! 🚀**
