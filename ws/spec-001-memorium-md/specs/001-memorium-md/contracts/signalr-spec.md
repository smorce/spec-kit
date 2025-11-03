# Memorium SignalR Specification

## Hub: `/hubs/journal`

| イベント | 方向 | 説明 |
|----------|------|------|
| `sessionStateUpdated` | Server → Client | セッション状態とプレビュー更新を通知 |
| `assistantPrompt` | Server → Client | 深掘り質問メッセージをリアルタイムで送信 |
| `userMessagePosted` | Client → Server | ユーザー入力を投稿し、サーバーがNATS経由で処理開始 |
| `previewReady` | Server → Client | プレビューが承認待ち状態になったことを告知 |
| `sessionClosed` | Server → Client | 承認後にセッションがクローズ済みであることを通知 |

### `sessionStateUpdated`

```json
{
  "sessionId": "uuid",
  "status": "draft|previewing|ready|committed",
  "pendingQuestions": [
    {
      "id": "uuid",
      "content": "string"
    }
  ],
  "lastActivity": "ISO-8601 date-time"
}
```

### `assistantPrompt`

```json
{
  "sessionId": "uuid",
  "promptId": "uuid",
  "content": "string",
  "suggestedReplyType": "text|choice"
}
```

### `userMessagePosted`

```json
{
  "sessionId": "uuid",
  "content": "string",
  "clientTimestamp": "ISO-8601 date-time"
}
```

サーバーは受信後に`messages.post` REST APIへフォールバックし、結果をイベントとして再配信する。

### `previewReady`

```json
{
  "sessionId": "uuid",
  "preview": {
    "importance": 5,
    "memoryTypes": {
      "semantic": ["string"],
      "episodic": ["string"]
    },
    "structuredJournal": "string",
    "summary": "string",
    "commentary": "string"
  }
}
```

### `sessionClosed`

```json
{
  "sessionId": "uuid",
  "memoryId": "uuid",
  "closedAt": "ISO-8601 date-time"
}
```

## Hub: `/hubs/search`

| イベント | 方向 | 説明 |
|----------|------|------|
| `searchRequested` | Client → Server | 検索リクエストを開始 |
| `searchProgress` | Server → Client | 3系統検索の進行状況を段階的に返却 |
| `searchCompleted` | Server → Client | 結果結合後の最終応答 |
| `searchFailed` | Server → Client | エラー通知（再試行ガイダンス付き） |

### `searchRequested`

```json
{
  "requestId": "uuid",
  "query": "string",
  "filters": {
    "importance": 6,
    "from": "YYYY-MM-DD",
    "to": "YYYY-MM-DD"
  }
}
```

### `searchProgress`

```json
{
  "requestId": "uuid",
  "source": "keyword|semantic|relation",
  "status": "running|completed|skipped",
  "resultCount": 12
}
```

### `searchCompleted`

```json
{
  "requestId": "uuid",
  "sources": [
    {
      "source": "keyword",
      "results": [
        {
          "memoryId": "uuid",
          "summary": "string",
          "score": 0.78,
          "snippet": "string",
          "metadata": {
            "importance": 7,
            "createdAt": "ISO-8601 date-time",
            "memoryTypes": {
              "semantic": ["value"],
              "episodic": []
            },
            "sourceField": "description"
          }
        }
      ]
    }
  ]
}
```

### `searchFailed`

```json
{
  "requestId": "uuid",
  "message": "string",
  "retryable": true
}
```

## 接続要件

- 認証は未実装（MVP）。セッション維持はSignalRの接続ID単位で管理する。
- 最大同時接続数は5（ローカル開発想定）。超過した場合はサーバー側で古い接続をクローズする。
- Keep-Alive間隔は30秒、タイムアウトは120秒。
