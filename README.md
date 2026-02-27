# Friend

多拠点型コンシェルジュチャットプラットフォーム。
スタッフがペルソナ（コンシェルジュ）としてユーザーとチャットで対話するサービスです。

## システム構成

```
frontend-user/    → ポート 3000（ユーザー向け）
frontend-staff/   → ポート 3001（スタッフ/管理者向け）
backend/          → ポート 8000（共通API - FastAPI）
db                → ポート 5432（PostgreSQL）
redis             → ポート 6379（Redis）
proxy-node-1/2    → Nginx プロキシ（スタッフIP隠匿）
```

## 技術スタック

| 領域 | 技術 |
|------|------|
| バックエンド | FastAPI / SQLAlchemy / Alembic |
| データベース | PostgreSQL 16 / Redis 7 |
| フロントエンド | Next.js / Tailwind CSS |
| インフラ | Docker Compose / Nginx |

## セットアップ

### 必要なもの

- Docker / Docker Compose

### 開発環境

```bash
# 全サービス起動
docker compose up -d

# マイグレーション実行
docker compose exec api alembic upgrade head

# テストデータ投入
docker compose exec api python -m scripts.seed
```

起動後:
- ユーザー画面: http://localhost:3000
- スタッフ管理画面: http://localhost:3001
- API: http://localhost:8080（プロキシ経由）

テストアカウント:

| ロール | メール | パスワード |
|--------|--------|-----------|
| admin | admin@example.com | admin1234 |
| staff | staff@example.com | staff1234 |
| user | user@example.com | user1234 |

## 主な機能

### ユーザー側

- アカウント登録・ログイン
- ペルソナ（コンシェルジュ）の検索・閲覧
- 1対1チャット（リアルタイムポーリング）
- いいね・足跡
- クレジット（ポイント）管理
- 招待リンクからの自動登録

### スタッフ/管理者側

- オペレーターチャット（複数セッション並行対応）
- ペルソナ管理（作成・編集）
- テンプレート（定型文）管理
- ユーザー管理・年齢認証
- 招待トークン発行
- メール配信設定
- LINE Bot 連携管理

## ディレクトリ構成

```
backend/              FastAPI バックエンド
├── app/
│   ├── models/       SQLAlchemy モデル（15テーブル）
│   ├── routers/      APIルーター（16個）
│   ├── schemas/      Pydantic スキーマ
│   └── services/     ビジネスロジック
├── alembic/          DBマイグレーション
└── requirements.txt

frontend-user/        ユーザー向け Next.js アプリ
├── src/app/          ページ（12画面）
├── src/components/   共通コンポーネント
└── src/lib/          API通信・認証

frontend-staff/       スタッフ管理 Next.js アプリ
├── src/app/          ページ（13画面）
├── src/components/   共通コンポーネント
└── src/lib/          API通信・認証

proxy/                Nginx リバースプロキシ設定
deploy/               本番デプロイ設定（Nginx + SSL）
```

## 認証・認可

JWT トークンベースの認証。3つのロール:

| ロール | 説明 |
|--------|------|
| user | 一般ユーザー |
| staff | オペレーター（担当ペルソナのチャット対応） |
| admin | 管理者（全機能アクセス可） |

## 本番デプロイ

詳細な手順は `deploy/DEPLOY.md` を参照。

### 1. 環境変数ファイルの作成

```bash
cat > .env.prod << 'EOF'
SECRET_KEY=<ランダムな長い文字列>
POSTGRES_PASSWORD=<強いパスワード>
FRONTEND_API_URL=http://<サーバーIP>:8080
ALLOWED_ORIGINS=http://<サーバーIP>:3000,http://<サーバーIP>:3001
EOF
```

SECRET_KEY の生成:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

> SSL 構築後は `FRONTEND_API_URL` と `ALLOWED_ORIGINS` を `https://` のドメインに変更してください。

### 2. 起動

```bash
# ビルド & 起動
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build

# マイグレーション
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api alembic upgrade head

# テストデータ投入
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api python -m scripts.seed
```

### 3. 更新時

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api alembic upgrade head
```

### 4. SSL 切り替え

Nginx + Let's Encrypt の構築後、`.env.prod` を更新:

```
FRONTEND_API_URL=https://api.example.com
ALLOWED_ORIGINS=https://app.example.com,https://staff.example.com
```

```bash
# フロントエンドは再ビルド（NEXT_PUBLIC_API_URL がビルド時に埋め込まれるため）
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build frontend-user frontend-staff

# API は再作成のみ
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --force-recreate api
```

## ライセンス

Private
