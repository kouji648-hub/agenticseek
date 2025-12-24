# AgenticSeek - Chat機能ドキュメント

## 📋 概要

AgenticSeek に追跡質問機能を持つチャット機能を実装しました。この機能により、ユーザーはAIと自然な会話ができ、AIが自動的に関連する追跡質問を提案します。

---

## 🎯 主な機能

### 1. リアルタイムチャット
- DeepSeek LLM を使用した自然言語処理
- 会話履歴の保持とコンテキスト管理
- セッション単位での会話管理

### 2. 追跡質問の自動生成
- 会話の文脈に基づいて3つの関連質問を自動生成
- ワンクリックで追跡質問を送信可能
- ユーザーの興味に合わせた質問提案

### 3. セッション管理
- 複数の会話セッションを保持
- セッションの作成、取得、削除機能
- セッションIDによる会話の復元

---

## 🏗️ アーキテクチャ

### バックエンド（Python + FastAPI）

#### データモデル

```python
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class ConversationSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

class ChatRequest(BaseModel):
    session_id: Optional[str]
    message: str
    generate_followup: bool = True

class ChatResponse(BaseModel):
    session_id: str
    message: str
    followup_questions: Optional[List[str]]
    timestamp: datetime
```

#### APIエンドポイント

| エンドポイント | メソッド | 説明 |
|------------|------|------|
| `/chat/message` | POST | チャットメッセージ送信と応答受信 |
| `/chat/sessions` | GET | 全セッション一覧取得 |
| `/chat/session/{id}` | GET | 特定セッション取得 |
| `/chat/session/{id}` | DELETE | セッション削除 |

---

## 📡 API使用方法

### チャットメッセージ送信

**エンドポイント:** `POST /chat/message`

**リクエスト:**
```json
{
  "session_id": "optional-uuid",
  "message": "こんにちは！AgenticSeekについて教えてください。",
  "generate_followup": true
}
```

**レスポンス:**
```json
{
  "session_id": "d34060db-7c9f-4eb8-bc4c-948c398dd686",
  "message": "こんにちは！AgenticSeekは自律型AIエージェントプラットフォームです...",
  "followup_questions": [
    "特定の分野でおすすめのAIエージェントはありますか？",
    "どのように活用できますか？",
    "導入時の注意点は？"
  ],
  "timestamp": "2025-12-24T20:23:04.292823"
}
```

### セッション一覧取得

**エンドポイント:** `GET /chat/sessions`

**レスポンス:**
```json
{
  "sessions": [
    {
      "session_id": "d34060db-7c9f-4eb8-bc4c-948c398dd686",
      "message_count": 4,
      "created_at": "2025-12-24T20:23:04.292823",
      "updated_at": "2025-12-24T20:25:15.123456"
    }
  ]
}
```

### セッション取得

**エンドポイント:** `GET /chat/session/{session_id}`

**レスポンス:**
```json
{
  "session_id": "d34060db-7c9f-4eb8-bc4c-948c398dd686",
  "messages": [
    {
      "role": "user",
      "content": "こんにちは",
      "timestamp": "2025-12-24T20:23:04.292823"
    },
    {
      "role": "assistant",
      "content": "こんにちは！お手伝いできることはありますか？",
      "timestamp": "2025-12-24T20:23:05.123456"
    }
  ],
  "created_at": "2025-12-24T20:23:04.292823",
  "updated_at": "2025-12-24T20:23:05.123456"
}
```

---

## 💻 フロントエンド実装

### Chat コンポーネント

**場所:** `client/src/components/Chat.tsx`

**主な機能:**
1. メッセージ送受信UI
2. 会話履歴の表示
3. 追跡質問ボタンの表示と送信
4. セッション管理
5. エラーハンドリング

**Props:**
```typescript
interface ChatProps {
  apiBaseUrl?: string;  // デフォルト: "http://localhost:7777"
}
```

### 使用方法

```tsx
import Chat from "@/components/Chat";

function MyApp() {
  return (
    <div>
      <Chat apiBaseUrl="http://localhost:7777" />
    </div>
  );
}
```

### UIコンポーネント

- **メッセージ表示エリア**: スクロール可能な会話履歴
- **入力フィールド**: メッセージ入力用テキストボックス
- **送信ボタン**: メッセージ送信
- **追跡質問ボタン**: 提案された質問をクリックで送信
- **クリアボタン**: 会話履歴のクリア

---

## 🔧 技術仕様

### バックエンド

- **言語**: Python 3.12
- **フレームワーク**: FastAPI 0.104.1
- **LLM**: DeepSeek Chat API
- **HTTP クライアント**: httpx 0.25.2
- **データ管理**: インメモリ（Dict型）

### フロントエンド

- **言語**: TypeScript
- **フレームワーク**: React 19
- **UI ライブラリ**: shadcn/ui, Tailwind CSS
- **アイコン**: Lucide React
- **スタイリング**: Tailwind CSS 4

---

## 📊 データフロー

```
User Input
    ↓
Frontend (Chat Component)
    ↓
POST /chat/message
    ↓
Backend API
    ↓
DeepSeek LLM API
    ├→ Generate Response
    └→ Generate Follow-up Questions
    ↓
Response
    ↓
Frontend Update
    ├→ Display Message
    └→ Show Follow-up Buttons
```

---

## 🚀 セットアップと起動

### 1. バックエンド起動

```bash
cd ~/agenticseek
source venv/bin/activate
python server/api.py
```

### 2. フロントエンド起動

```bash
cd ~/agenticseek
npm run dev
```

### 3. ブラウザで確認

```
http://localhost:3002/
```

「💬 Chat」タブをクリックしてチャット機能を使用

---

## 🧪 テスト

### cURLでのテスト

```bash
# 基本的なチャットテスト
curl -X POST 'http://localhost:7777/chat/message' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "こんにちは！",
    "generate_followup": true
  }'

# セッション一覧取得
curl http://localhost:7777/chat/sessions

# 特定セッション取得
curl http://localhost:7777/chat/session/{session_id}
```

### フロントエンドでのテスト

1. http://localhost:3002/ にアクセス
2. 「💬 Chat」タブをクリック
3. メッセージを入力して送信
4. AIの応答と追跡質問を確認
5. 追跡質問ボタンをクリックして会話を続ける

---

## 🔐 環境変数

```bash
# DeepSeek API キー
DEEPSEEK_API_KEY=sk-d8d78811ea69434fad5d447b5c1027e3

# API ベース URL（フロントエンド）
VITE_API_BASE_URL=http://localhost:7777

# ポート番号
PORT=7777
```

---

## 📈 今後の改善案

### 優先度 1
- [ ] データベース統合（PostgreSQL/MongoDB）
- [ ] セッション永続化
- [ ] ユーザー認証との統合

### 優先度 2
- [ ] メッセージの編集・削除機能
- [ ] 会話のエクスポート（PDF/Markdown）
- [ ] コードハイライト表示

### 優先度 3
- [ ] 音声入力対応
- [ ] マルチモーダル対応（画像アップロード）
- [ ] リアルタイムストリーミング応答

---

## 🐛 トラブルシューティング

### エラー: "DeepSeek API error"

**原因:** APIキーが無効または期限切れ

**解決策:**
```bash
# 環境変数を確認
echo $DEEPSEEK_API_KEY

# APIキーを更新
export DEEPSEEK_API_KEY=your-new-key
```

### エラー: "Session not found"

**原因:** セッションIDが存在しない

**解決策:**
- 新しいセッションを作成（session_id を null に設定）
- または有効なセッションIDを使用

### フロントエンドでメッセージが表示されない

**原因:** CORS設定またはAPIベースURL設定の問題

**解決策:**
1. バックエンドのCORS設定を確認
2. `VITE_API_BASE_URL` 環境変数を確認
3. ブラウザのコンソールでエラーを確認

---

## 📝 変更履歴

### 2025-12-24
- ✅ 初版リリース
- ✅ チャット機能実装
- ✅ 追跡質問自動生成機能実装
- ✅ セッション管理機能実装
- ✅ フロントエンドUI実装

---

## 📞 サポート

問題が発生した場合：
- GitHub Issues: https://github.com/kouji648-hub/agenticseek/issues
- ドキュメント: `README.md`, `CLAUDE_HANDOFF.md`

---

**追跡質問機能を活用して、より自然で効果的なAI会話体験をお楽しみください！** 🚀
