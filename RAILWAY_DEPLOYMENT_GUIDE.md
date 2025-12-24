# Railway デプロイメントガイド

AgenticSeek バックエンド API を Railway にデプロイする手順

---

## 📋 前提条件

- GitHub アカウント
- GitHub リポジトリに `server/` がプッシュされている
- Railway アカウント（無料で作成可能）

---

## 🚀 デプロイ手順

### ステップ 1: Railway アカウントを作成

1. **Railway にアクセス**
   - URL: https://railway.app/
   - 「Start a New Project」をクリック

2. **GitHub でサインイン**
   - 「Login with GitHub」をクリック
   - GitHub アカウントで認証

### ステップ 2: 新しいプロジェクトを作成

1. **「New Project」をクリック**

2. **「Deploy from GitHub repo」を選択**

3. **リポジトリを選択**
   - `kouji648-hub/agenticseek` を選択
   - もし表示されない場合は「Configure GitHub App」をクリックしてリポジトリへのアクセスを許可

4. **デプロイする環境を選択**
   - 「Add variables」をクリック

### ステップ 3: 環境変数を設定

以下の環境変数を設定します：

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `PORT` | `7777` | API サーバーのポート |
| `DEEPSEEK_API_KEY` | `sk-d8d78811ea69434fad5d447b5c1027e3` | DeepSeek API キー |
| `PYTHONUNBUFFERED` | `1` | Python ログ出力設定 |

**設定方法:**
1. Railway プロジェクトダッシュボードで「Variables」タブをクリック
2. 「New Variable」をクリック
3. 上記の変数を一つずつ追加

### ステップ 4: デプロイ設定

1. **Settings タブを開く**
   - 「Root Directory」を設定: `/server`
   - 「Build Command」は自動検出（Dockerfile を使用）
   - 「Start Command」: `python api.py`

2. **ドメイン設定**
   - 「Settings」→「Networking」
   - 自動生成されたドメインが表示される（例: `agenticseek-production.up.railway.app`）
   - カスタムドメインも設定可能

### ステップ 5: デプロイを実行

1. **自動デプロイ**
   - Railway は GitHub にプッシュすると自動的にデプロイを開始
   - デプロイログは「Deployments」タブで確認可能

2. **デプロイステータス確認**
   - ✅ Building → Running: 成功
   - ❌ Failed: ログを確認してエラーを修正

### ステップ 6: API をテスト

1. **デプロイされた URL を確認**
   - Railway ダッシュボードで「Settings」→「Domains」
   - 例: `https://agenticseek-production.up.railway.app`

2. **Health Check**
   ```bash
   curl https://your-app.up.railway.app/health
   ```

   期待される結果:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-12-24T...",
     "version": "1.0.0"
   }
   ```

3. **API ドキュメントにアクセス**
   ```
   https://your-app.up.railway.app/docs
   ```

4. **テストリクエスト**
   ```bash
   curl -X POST https://your-app.up.railway.app/browse \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.google.com",
       "action": "screenshot"
     }'
   ```

---

## 🔧 トラブルシューティング

### ❌ Playwright のインストールエラー

**エラー:**
```
Error: Failed to install browsers
```

**解決策:**
Dockerfile で Playwright の依存関係がインストールされていることを確認:
```dockerfile
RUN playwright install chromium
RUN playwright install-deps chromium
```

### ❌ ポートエラー

**エラー:**
```
Error: Port 7777 is already in use
```

**解決策:**
環境変数 `PORT` が正しく設定されているか確認。Railway は自動的に `PORT` 環境変数を設定します。

### ❌ メモリ不足

**エラー:**
```
Process killed (OOM)
```

**解決策:**
1. Railway プランをアップグレード（Hobby プランで 8GB RAM）
2. Playwright のヘッドレスモードを有効化
3. 同時実行数を制限

### ❌ API キーエラー

**エラー:**
```
DeepSeek API authentication failed
```

**解決策:**
環境変数 `DEEPSEEK_API_KEY` が正しく設定されているか確認。

---

## 📊 Railway の料金プラン

### Hobby プラン（推奨）
- **料金**: $5/月
- **リソース**: 8GB RAM, 8 vCPU
- **実行時間**: 制限なし
- **カスタムドメイン**: 対応

### Trial プラン（無料）
- **料金**: 無料
- **リソース**: 制限あり
- **実行時間**: 月 500 時間まで
- **カスタムドメイン**: 非対応

詳細: https://railway.app/pricing

---

## 🌐 フロントエンドとの連携

### 環境変数の更新

デプロイ後、フロントエンドの環境変数を更新:

**ローカル開発（`.env`）:**
```bash
VITE_API_BASE_URL=https://your-app.up.railway.app
```

**Netlify（本番環境）:**
1. Netlify ダッシュボードを開く
2. 「Site settings」→「Environment variables」
3. `VITE_API_BASE_URL` を追加:
   ```
   https://your-app.up.railway.app
   ```

### CORS 設定の確認

`server/api.py` で CORS が正しく設定されているか確認:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のドメインに制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔄 継続的デプロイ（CD）

Railway は GitHub と連携して自動デプロイを実行:

1. **コードを更新**
   ```bash
   git add .
   git commit -m "Update API"
   git push origin main
   ```

2. **自動デプロイ**
   - Railway が自動的に変更を検知
   - ビルドとデプロイを実行
   - 数分でデプロイ完了

3. **ロールバック**
   - Railway ダッシュボードで以前のデプロイメントを選択
   - 「Redeploy」をクリック

---

## 📝 デプロイ後のチェックリスト

- [ ] API が正常に起動している（`/health` エンドポイント確認）
- [ ] 環境変数が正しく設定されている
- [ ] API ドキュメントにアクセスできる（`/docs`）
- [ ] ブラウザ自動化が動作する（Playwright）
- [ ] フロントエンドから API に接続できる
- [ ] CORS が正しく設定されている
- [ ] エラーログを確認（Railway ダッシュボード）

---

## 🔗 リンク

- **Railway 公式サイト**: https://railway.app/
- **Railway ドキュメント**: https://docs.railway.app/
- **GitHub リポジトリ**: https://github.com/kouji648-hub/agenticseek
- **Netlify フロントエンド**: https://agenticseek-pibmxpgd.manus.space/

---

## 📞 次のステップ

1. ✅ Railway にデプロイ完了
2. ⏭️ Netlify にフロントエンドをデプロイ
3. ⏭️ カスタムドメインを設定
4. ⏭️ モニタリングとログ設定
5. ⏭️ データベース統合（オプション）

---

**デプロイが完了したら、フロントエンドを Netlify にデプロイして統合テストを実行してください！** 🚀
