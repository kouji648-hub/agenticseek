# AgenticSeek - Netlify デプロイメントガイド

このガイドでは、AgenticSeek フロントエンドを Netlify にデプロイする手順を説明します。

## 前提条件

- GitHub アカウント
- Netlify アカウント（https://netlify.com）
- GitHub リポジトリへのアクセス権

## デプロイ手順

### 方法 1: Netlify UI を使用（推奨）

#### ステップ 1: Netlify にログイン

1. https://app.netlify.com にアクセス
2. GitHub アカウントでログイン

#### ステップ 2: 新しいサイトを作成

1. **"Add new site"** をクリック
2. **"Import an existing project"** を選択
3. **"GitHub"** を選択

#### ステップ 3: リポジトリを選択

1. GitHub アカウントを認可
2. `agenticseek` リポジトリを選択

#### ステップ 4: ビルド設定を確認

自動的に以下が検出されます：

- **Build command**: `npm run build`
- **Publish directory**: `dist/public`

これらが正しいことを確認してください。

#### ステップ 5: 環境変数を設定

**"Advanced build settings"** で以下の環境変数を設定：

```
VITE_API_BASE_URL=https://api.agenticseek.com
```

#### ステップ 6: デプロイ

**"Deploy site"** をクリック

デプロイが完了すると、Netlify が自動的に URL を生成します。

### 方法 2: Netlify CLI を使用

#### ステップ 1: Netlify CLI をインストール

```bash
npm install -g netlify-cli
```

#### ステップ 2: Netlify にログイン

```bash
netlify login
```

#### ステップ 3: サイトを初期化

```bash
cd agenticseek
netlify init
```

対話的に以下を設定：

- **Build command**: `npm run build`
- **Publish directory**: `dist/public`
- **Functions directory**: `netlify/functions`

#### ステップ 4: 環境変数を設定

```bash
netlify env:set VITE_API_BASE_URL "https://api.agenticseek.com"
```

#### ステップ 5: デプロイ

```bash
netlify deploy --prod
```

## カスタムドメインの設定

### ステップ 1: Netlify ダッシュボードにアクセス

1. https://app.netlify.com にアクセス
2. デプロイしたサイトを選択

### ステップ 2: ドメイン設定

1. **"Site settings"** → **"Domain management"** をクリック
2. **"Add custom domain"** をクリック
3. カスタムドメインを入力（例: `agenticseek.com`）

### ステップ 3: DNS レコードを設定

Netlify の指示に従って、DNS プロバイダーで以下のレコードを追加：

```
CNAME: www.agenticseek.com -> your-site-name.netlify.app
A: agenticseek.com -> 75.2.60.5
```

### ステップ 4: SSL 証明書を設定

Netlify は自動的に Let's Encrypt から SSL 証明書を取得します。

## バックエンド API の接続

### オプション 1: 外部 API サーバーを使用

バックエンド API を別のサーバーにデプロイし、`VITE_API_BASE_URL` で指定：

```bash
netlify env:set VITE_API_BASE_URL "https://api.your-domain.com"
```

推奨プラットフォーム：

- **Railway**: https://railway.app
- **Render**: https://render.com
- **Heroku**: https://www.heroku.com
- **AWS Lambda**: https://aws.amazon.com/lambda/
- **Google Cloud Run**: https://cloud.google.com/run

### オプション 2: Netlify Functions を使用

`netlify/functions/` ディレクトリ内のファイルは自動的に Netlify Functions としてデプロイされます。

例：`netlify/functions/agent.ts` は `/.netlify/functions/agent` でアクセス可能

## 環境変数の管理

### Netlify UI で設定

1. **Site settings** → **Build & deploy** → **Environment**
2. **Edit variables** をクリック
3. 環境変数を追加

### CLI で設定

```bash
# 環境変数を設定
netlify env:set KEY value

# 環境変数を確認
netlify env:list

# 環境変数を削除
netlify env:unset KEY
```

## デプロイメント履歴

### デプロイを確認

1. Netlify ダッシュボードで **"Deploys"** タブをクリック
2. デプロイ履歴が表示されます

### デプロイをロールバック

1. 前のデプロイをクリック
2. **"Restore this deploy"** をクリック

## パフォーマンス最適化

### キャッシング戦略

`netlify.toml` で以下が設定されています：

```toml
# 静的アセット（1年間キャッシュ）
Cache-Control = "public, max-age=31536000, immutable"

# HTML ファイル（キャッシュなし）
Cache-Control = "public, max-age=0, must-revalidate"
```

### CDN 最適化

- Netlify は自動的に 150+ の POP（Point of Presence）を使用
- グローバルな高速配信が可能

## セキュリティ

### セキュリティヘッダー

`netlify.toml` で以下が設定されています：

```toml
X-Frame-Options = "SAMEORIGIN"
X-Content-Type-Options = "nosniff"
X-XSS-Protection = "1; mode=block"
Referrer-Policy = "strict-origin-when-cross-origin"
```

### HTTPS

すべてのサイトは自動的に HTTPS で保護されます。

## トラブルシューティング

### ビルドが失敗する場合

1. ビルドログを確認
2. 依存関係が正しくインストールされているか確認
3. `npm run build` をローカルで実行してテスト

```bash
npm run build
```

### デプロイ後に 404 エラーが表示される

SPA ルーティングが正しく設定されているか確認：

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 環境変数が読み込まれない

1. 環境変数が正しく設定されているか確認
2. ビルドコマンドで環境変数を使用しているか確認
3. サイトを再デプロイ

```bash
netlify deploy --prod --clear-cache
```

## CI/CD パイプライン

### 自動デプロイ

GitHub にプッシュすると、自動的に Netlify がデプロイします：

1. GitHub にコミットをプッシュ
2. Netlify が自動的にビルドを開始
3. ビルドが成功するとデプロイ

### デプロイプレビュー

PR を作成すると、Netlify が自動的にプレビューサイトを生成します。

## 監視とログ

### デプロイログを確認

```bash
netlify logs
```

### ビルドログを確認

Netlify ダッシュボード → **Deploys** → デプロイを選択 → **Deploy log**

## 次のステップ

1. カスタムドメインを設定
2. バックエンド API をデプロイ
3. 本番環境でテスト
4. DNS を更新

## サポート

- Netlify ドキュメント: https://docs.netlify.com
- Netlify コミュニティ: https://community.netlify.com
- GitHub Issues: https://github.com/kouji648-hub/agenticseek/issues

---

**Happy Deploying! 🚀**
