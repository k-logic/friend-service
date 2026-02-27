# 多拠点型コンシェルジュプラットフォーム - 実装計画

## 概要
FastAPI + Next.js + PostgreSQL + Redis による多拠点型コンシェルジュチャットプラットフォーム。
Docker Compose で全サービスを管理。

---

## ステップ1: インフラ・バックエンド基盤

### 1-1. プロジェクト構造の作成
```
friend/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI エントリーポイント
│   │   ├── config.py          # 設定管理
│   │   ├── database.py        # DB接続・セッション管理
│   │   ├── models/            # SQLAlchemy モデル
│   │   │   ├── account.py
│   │   │   ├── persona.py
│   │   │   ├── session.py
│   │   │   └── message.py
│   │   ├── schemas/           # Pydantic スキーマ
│   │   ├── routers/           # APIルーター
│   │   │   ├── auth.py
│   │   │   ├── messages.py
│   │   │   ├── personas.py
│   │   │   └── credits.py
│   │   └── services/          # ビジネスロジック
│   │       ├── credit_service.py
│   │       └── message_service.py
│   └── alembic/               # DBマイグレーション
│       └── versions/
├── frontend/
│   ├── Dockerfile
│   └── (Next.js プロジェクト)
├── proxy/
│   ├── Dockerfile
│   └── nginx.conf             # プロキシノード設定
└── PLAN.md
```

### 1-2. docker-compose.yml
以下のサービスを定義:
- **api**: FastAPI バックエンド (ポート 8000)
- **db**: PostgreSQL (ポート 5432) - アカウント・決済データ
- **redis**: Redis (ポート 6379) - セッションキャッシュ・レート制限
- **proxy-node-1, proxy-node-2**: Nginx プロキシノード
- **frontend**: Next.js (ポート 3000)
- カスタムネットワーク: `proxy-net`, `internal-net` で論理分離

### 1-3. DBスキーマ (Alembic マイグレーション)

**accounts テーブル:**
- id, email, display_name, hashed_password
- credit_balance (integer, default 0)
- role (enum: user/staff/admin)
- status (enum: active/suspended)
- created_at, updated_at

**personas テーブル:**
- id, staff_account_id (FK → accounts)
- name, avatar_url, bio, attributes (JSONB)
- is_active (boolean)
- created_at, updated_at

**sessions テーブル:**
- id, user_account_id (FK → accounts)
- persona_id (FK → personas)
- status (enum: active/closed)
- created_at, updated_at

**messages テーブル:**
- id (BIGINT, 高速インデックス用)
- session_id (FK → sessions)
- sender_type (enum: user/persona)
- sender_id (integer)
- content (text)
- credit_cost (integer)
- created_at
- INDEX: (session_id, id) で差分ポーリング高速化

### 1-4. 差分ポーリングAPI
`GET /api/v1/messages/poll`
- パラメータ: `session_id`, `last_message_id`
- レスポンス: last_message_id 以降の新着メッセージ配列
- クレジット減算はメッセージ送信時(`POST /api/v1/messages`)にトランザクション処理

### 1-5. プロキシノード構成
- Nginx ベースの2ノード構成
- 各ノードは独立サブネット上に配置
- ヘルスチェック付きアップストリーム設定
- X-Forwarded-For ヘッダーの書き換えでスタッフIP隠匿

---

## ステップ2: フロントエンド (次フェーズ)

### 2-1. Next.js マルチロールダッシュボード
- スタッフ用: ペルソナ切替・複数チャット並行管理
- ユーザー用: チャットUI・クレジット残高表示
- 差分ポーリングによるメッセージ更新

### 2-2. テンプレート機能
- 定型文管理・名前差し替え

---

## 実装順序
1. docker-compose.yml + 各 Dockerfile 作成
2. FastAPI 基盤 (config, database, models)
3. Alembic マイグレーション
4. APIエンドポイント実装 (messages/poll, messages/send, credits)
5. プロキシノード設定
6. フロントエンド (ステップ2)
