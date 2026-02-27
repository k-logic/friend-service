# デプロイ手順

## サーバー構成

```
[ユーザー] → [プロキシサーバー (Nginx + SSL)] → [アプリサーバー (Docker)]
                 別マシン                            別マシン
```

- **プロキシサーバー**: Nginx + Let's Encrypt（SSL終端）
- **アプリサーバー**: Docker Compose で全サービス稼働

## 前提
- プロキシサーバーに Nginx がインストール済み
- アプリサーバーに Docker / Docker Compose がインストール済み
- ドメイン3つの DNS が設定済み（A レコードがプロキシサーバーのIPを指す）
  - `app.example.com` — ユーザー向けフロントエンド
  - `staff.example.com` — スタッフ管理画面
  - `api.example.com` — API
- プロキシサーバーからアプリサーバーへの内部ネットワーク接続が可能

---

## アプリサーバー側

### 1. 環境変数ファイルの作成

```bash
cd /path/to/friend

cat > .env.prod << 'EOF'
SECRET_KEY=ここにランダムな文字列を設定
POSTGRES_PASSWORD=ここに強いパスワードを設定
FRONTEND_API_URL=http://<サーバーIP>:8080
ALLOWED_ORIGINS=http://<サーバーIP>:3000,http://<サーバーIP>:3001
EOF
```

SECRET_KEY の生成例:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

> SSL 構築後は `FRONTEND_API_URL` と `ALLOWED_ORIGINS` を `https://` のドメインに変更してください。

### 2. ファイアウォール設定

プロキシサーバーのIPからのみアクセスを許可:

```bash
# UFW の例
sudo ufw allow from <プロキシサーバーIP> to any port 3000
sudo ufw allow from <プロキシサーバーIP> to any port 3001
sudo ufw allow from <プロキシサーバーIP> to any port 8080
```

DB(5432) と Redis(6379) は `127.0.0.1` にバインドされるので外部からはアクセスできません。

### 3. アプリケーション起動

```bash
# ビルド & 起動
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build

# マイグレーション実行
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api alembic upgrade head

# テストデータ投入（必要な場合）
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api python -m scripts.seed

# ログ確認
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod logs -f
```

---

## プロキシサーバー側

### 4. DNS 設定

3つのサブドメインの A レコードを**プロキシサーバーのグローバルIP**に向ける:

| レコード | ホスト名 | 値 |
|---------|---------|-----|
| A | app.example.com | プロキシサーバーのグローバルIP |
| A | staff.example.com | プロキシサーバーのグローバルIP |
| A | api.example.com | プロキシサーバーのグローバルIP |

反映確認:
```bash
dig +short app.example.com
```

### 5. Nginx 設定

設定ファイルをコピーし、2箇所を置換:
- `example.com` → 実際のドメイン
- `APP_SERVER_IP` → アプリサーバーの内部IPアドレス

```bash
# 設定ファイルをコピー
sudo cp deploy/nginx/friend.conf /etc/nginx/sites-available/friend

# ドメイン名を一括置換（例: example.com → yourdomain.com）
sudo sed -i 's/example.com/yourdomain.com/g' /etc/nginx/sites-available/friend

# アプリサーバーIPを置換（例: 192.168.1.100）
sudo sed -i 's/APP_SERVER_IP/192.168.1.100/g' /etc/nginx/sites-available/friend

# 有効化
sudo ln -s /etc/nginx/sites-available/friend /etc/nginx/sites-enabled/
```

### 6. SSL 証明書の取得（Let's Encrypt）

初回は SSL 証明書がまだないので段階的にセットアップ:

```bash
# 1. 各設定ファイルの listen 443 ブロック全体を一時的にコメントアウト
# 2. Nginx 再読み込み
sudo nginx -t && sudo systemctl reload nginx

# 3. certbot で証明書取得
sudo certbot --nginx -d app.yourdomain.com -d staff.yourdomain.com -d api.yourdomain.com

# 4. コメントアウトした 443 ブロックを元に戻す
# 5. Nginx 再読み込み
sudo nginx -t && sudo systemctl reload nginx

# 自動更新の確認
sudo certbot renew --dry-run
```

---

## 動作確認

```bash
# API ヘルスチェック
curl https://api.yourdomain.com/health

# ブラウザで確認
# https://app.yourdomain.com — ユーザー画面
# https://staff.yourdomain.com — スタッフ管理画面
```

## 更新時

```bash
# アプリサーバーで実行
cd /path/to/friend
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod exec api alembic upgrade head
```

## ポート一覧

| サービス | ポート | 外部公開 | 用途 |
|---------|--------|---------|------|
| frontend-user | 3000 | プロキシから | ユーザーフロントエンド |
| frontend-staff | 3001 | プロキシから | スタッフ管理画面 |
| proxy-node-1 | 8080 | プロキシから | APIプロキシ |
| proxy-node-2 | 8081 | プロキシから | APIプロキシ（予備） |
| api | 8000 | ローカルのみ | FastAPI バックエンド |
| db | 5432 | ローカルのみ | PostgreSQL |
| redis | 6379 | ローカルのみ | Redis |
