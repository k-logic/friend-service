# Friend - 何を作るのか

## プロジェクト概要
多拠点型コンシェルジュチャットプラットフォーム。
スタッフがペルソナ（コンシェルジュ）としてユーザーとチャットで対話するサービス。

---

## システム構成

```
frontend-user/    → ポート 3000（ユーザー向け）
frontend-staff/   → ポート 3001（スタッフ/管理者向け）
backend/          → ポート 8000（共通API）
db (PostgreSQL)   → ポート 5432
redis             → ポート 6379
proxy-node-1/2    → Nginx プロキシ（スタッフIP隠匿）
```

---

## ユーザー側（frontend-user）
顧客が使うチャットアプリ。参考UIイメージは `frontend-user-image/` に格納。

### UIレイアウト（参考イメージより）

**共通レイアウト: 左サイドバー + メインエリア**

左サイドバー（全画面共通・固定）:
- サービスロゴ
- ユーザーアバター・表示名・会員ID
- ポイント（クレジット）残高 + 購入ボタン
- ナビメニュー: さがす / メッセージ / いいね / 足跡 / マイページ / ポイント購入 / お知らせ / お問い合わせ / その他 / ログアウト

**画面一覧:**

| 画面 | パス | 説明 |
|------|------|------|
| さがす | `/search` | ペルソナをグリッド（サークルアバター）でブラウズ・検索 |
| ペルソナ詳細 | `/persona/[id]` | ペルソナのプロフィール表示、いいね・足跡記録、チャット開始 |
| メッセージ一覧 | `/messages` | やり取り中のペルソナ一覧（activeセッションのみ表示）。アバター・名前・年齢・日時・最新ペルソナ返信プレビュー（15文字）表示 |
| チャット | `/chat/[id]` | 吹き出し形式。ペルソナ側=ピンク/左寄せ、ユーザー側=ベージュ/右寄せ。送信者名（ユーザー名/ペルソナ名）表示 |
| いいね | `/likes` | いいね一覧（ページロード時にサーバーから状態取得） |
| 足跡 | `/footprints` | 閲覧履歴 |
| マイページ | `/mypage` | プロフィール編集 |
| ポイント購入 | `/credits` | クレジットチャージ |
| お知らせ | `/notifications` | システム通知 |
| お問い合わせ | `/contact` | サポート連絡 |
| 招待登録 | `/invite` | 招待メールからの自動登録ページ（認証不要） |

### 機能一覧

| 機能 | 説明 |
|------|------|
| アカウント管理 | 新規登録・ログイン・プロフィール編集 |
| 招待メール登録 | 招待URLクリック → 表示名入力 → 自動登録 → TOP遷移 |
| ペルソナ一覧・選択 | コンシェルジュをブラウズして選ぶ |
| チャット | 1対1チャット（差分ポーリング）、画像添付対応 |
| クレジット残高表示 | サイドバーに常時表示 |
| クレジット購入 | チャージ（決済連携は後のフェーズ） |
| チャット履歴 | 過去のセッション閲覧 |
| いいね | ペルソナへのいいね |
| 足跡 | 閲覧履歴の確認 |

---

## オペレーション側（frontend-staff）
スタッフ・管理者が使う業務ツール。参考UIイメージは `frontend-staff-image/` に格納。

### UIレイアウト（参考イメージより）

**オペレーターチャット画面（メイン業務画面）:**
- 左側: チャット一覧テーブル（サイト種別、ペルソナ名、ユーザー名、ポイント残高、最終送受信日時）
- 右上: ユーザー最終送信内容の表示、全やり取り確認リンク
- 右中: テンプレート（%OPE01%, %OPE02% 等）の編集ボタン
- 右下: 送信フォーム（メッセージ入力、メディア添付、送信ボタン）
- メッセージの送信/閲覧はユーザ別設定（OPT）

**管理画面サイドバー（実装済み）:**

| セクション | 対象ロール | メニュー |
|-----------|-----------|---------|
| オペレーター | staff, admin | チャット、ペルソナ検索、テンプレート、お知らせ（未読バッジ付き） |
| ペルソナ管理 | admin のみ | ペルソナ一覧・作成 |
| ユーザ管理（検索） | staff, admin | ユーザ検索 |
| ユーザ管理（管理者） | admin のみ | 年齢認証管理 |
| 有料情報関連 | admin のみ | 有料情報管理 |
| メール関連 | admin のみ | メール配信、招待管理 |
| サポート | admin のみ | 問い合わせ管理 |
| LINE | admin のみ | LINE Bot管理 |

**画面一覧:**

| 画面 | パス | 対象ロール | 説明 |
|------|------|-----------|------|
| ログイン | `/login` | — | スタッフ/管理者専用認証 |
| チャット | `/operator` | staff, admin | メイン業務画面 |
| ペルソナ検索 | `/personas/search` | staff, admin | 全ペルソナの一覧・検索（閲覧のみ） |
| ペルソナ管理 | `/personas` | admin のみ | ペルソナ一覧・作成・編集（staffはリダイレクト） |
| テンプレート | `/templates` | staff, admin | 定型文の登録・編集 |
| お知らせ | `/notifications` | staff, admin | システム通知一覧・既読管理 |
| ユーザ検索 | `/admin/users` | staff, admin | ユーザー検索（staffは閲覧のみ、adminはステータス変更可） |
| 年齢認証管理 | `/admin/age-verification` | admin のみ | 年齢認証の承認/却下 |
| 有料情報管理 | `/admin/paid-contents` | admin のみ | 有料情報の設定 |
| メール配信 | `/admin/mail` | admin のみ | 一斉/予約/定期送信 |
| 招待管理 | `/admin/invitations` | admin のみ | 招待トークン発行・一覧 |
| 問い合わせ管理 | `/admin/inquiries` | admin のみ | 問い合わせ対応 |
| LINE Bot管理 | `/admin/line-bot` | admin のみ | Bot連携管理 |

**LINE Bot管理画面:**
- アカウント一覧（ID、状態、メモ、line bot id、Webhook URL、登録数、当月配信数）
- 操作: 編集、有効/無効切替、新規受入/配信可、検証、復旧

### 機能一覧

| 機能 | 対象ロール | 説明 |
|------|-----------|------|
| スタッフログイン | staff, admin | スタッフ/管理者専用認証（userロールはログイン不可） |
| ペルソナ検索 | staff, admin | 全ペルソナの一覧・検索（閲覧のみ） |
| ペルソナ管理 | admin のみ | 作成・編集（名前、アバター、自己紹介、属性） |
| 複数チャット並行対応 | staff, admin | チャット一覧から選択して返信。staffは自分の担当ペルソナのセッションのみ、adminは全セッション |
| テンプレート管理 | staff, admin | 定型文（%OPE01%等）の登録・編集・差し替え |
| メディア添付 | staff, admin | 送信フォームからメディアを選択して送信 |
| お知らせ通知 | staff, admin | システム通知（新規ユーザー登録等）の受信・既読管理。サイドバーに未読バッジ表示（30秒ポーリング） |
| 受信通知 | staff, admin | 新着メッセージのリアルタイム通知 |
| 招待管理 | admin のみ | 招待トークン発行（メールアドレス指定）、発行済み一覧、URLコピー |
| ユーザ管理 | admin のみ | 検索（性別・ステータス別）、追加、年齢認証、画像管理、ステータス別人数 |
| サポート問い合わせ管理 | admin のみ | 問い合わせ一覧、未返信フィルタ、一括返信/削除 |
| 有料情報管理 | admin のみ | 有料情報の設定・一覧 |
| メール配信管理 | admin のみ | 一斉/予約/定期送信、トリガーメール設定 |
| LINE Bot管理 | admin のみ | Bot連携アカウント管理、Webhook設定、有効/無効切替 |
| ダッシュボード | admin のみ | セッション数、応答時間などの統計 |

---

## 招待メール登録フロー

ユーザー獲得のための招待リンク機能。ペルソナとの紐付けは行わない（ユーザーが自分で選ぶ）。

### フロー
1. **admin** が招待管理画面でメールアドレスを指定してトークン発行
2. メールにURL (`http://localhost:3000/invite?token=xxx`) を記載して送信
3. **新規ユーザー** がURLクリック → トークン検証 → 表示名入力 → 自動登録 → `/search` へ遷移
4. **既存ユーザー**（メールアドレス重複）→ 登録不可エラー
5. 登録完了時に全staff/adminアカウントへ通知（notificationsテーブル経由）

### 招待登録ページ（`/invite`）のUX
- プロフィール設定トーン（「ようこそ! ニックネームを決めてサービスをはじめましょう」）
- メールアドレスは読み取り専用で表示（トークンから取得）
- 表示名入力 → 「サービスをはじめる」ボタン
- ログインリンクなし（招待前提のため不要）

### 技術詳細
- トークン: `secrets.token_urlsafe(32)` で生成、有効期限72時間
- パスワード: ランダム生成（`secrets.token_urlsafe(16)`）
- 登録後: JWT発行 → フロントで `setToken()` → `/api/v1/auth/me` でアカウント情報取得 → リダイレクト

---

## 共通バックエンド（backend）

### 認証・認可

テーブル分離済み: users（顧客）と staff_members（運営者）は別テーブル。JWTにtype（user/staff）を含む。
認証エンドポイントも分離: ユーザー `/api/v1/auth/*`、スタッフ `/api/v1/staff/auth/*`

4つの認証依存関数でロールベースアクセス制御:
- `get_current_account` — 全認証済みユーザー（user/staff/admin）、Union[User, StaffMember]を返す
- `get_current_user` — user のみ（staffトークンは401）
- `get_current_staff` — staff + admin のみ（userトークンは403）
- `get_current_admin` — admin のみ

### APIエンドポイント（16ルーター）

| 領域 | 認可 | 説明 |
|------|------|------|
| 認証API | なし | JWT発行、ロール判定（user / staff / admin） |
| メッセージAPI | account + セッション所有権チェック | 送信（POST）・差分ポーリング（GET）・クレジット減算。staff/adminはセッション所有権チェック免除 |
| ペルソナAPI（一覧・検索） | account | 全ペルソナ一覧取得 |
| ペルソナAPI（作成） | admin | ペルソナ新規作成 |
| ペルソナAPI（更新） | staff（自分の担当のみ）/ admin（全て） | ペルソナ編集 |
| ペルソナAPI（自分の担当） | staff | `/staff/mine` で自分が担当するペルソナ一覧 |
| クレジットAPI | account | 残高照会・チャージ・履歴 |
| クレジット付与API | admin | 管理者によるクレジット付与 |
| セッションAPI | account + ロール別フィルタ | 開始（既存activeセッションがあれば再利用）・終了・一覧（userは自分のみ、staffは担当ペルソナのみ、adminは全て） |
| いいねAPI | account | ペルソナへのいいね送信・一覧取得 |
| 足跡API | account | 閲覧記録の保存（upsert: 同一ユーザー×ペルソナは日時更新）・一覧取得 |
| お知らせAPI | account | システム通知の取得（未読フィルタ対応）・個別既読・一括既読 |
| お問い合わせAPI | account / admin | 問い合わせ送信（ユーザー側）・一覧/返信/一括返信/削除（admin側） |
| 招待API | admin（発行・一覧）/ なし（検証・登録） | トークン発行（POST）・一覧（GET）・検証（GET /{token}/verify）・登録（POST /{token}/register） |
| ユーザ管理API | staff（検索・閲覧）/ admin（変更・作成） | 検索（全体/性別/ステータス別）、追加、年齢認証管理、停止/退避、ステータス別人数集計 |
| 画像管理API | admin | アップロード画像の一覧・承認・削除 |
| 有料情報API | admin | 有料情報の設定・一覧取得 |
| メール配信API | admin | 一斉送信・予約送信・定期送信の作成/一覧、トリガーメール設定、遅延キュー確認 |
| LINE Bot API | admin | Botアカウント管理、Webhook設定、有効/無効切替、検証、登録数/配信数取得 |
| テンプレートAPI | staff | 定型文（%OPE01%等）のCRUD、変数差し替え |
| 年齢認証API | admin | 年齢認証の一覧・承認・却下 |

---

## DBスキーマ

- **users**: id, email, display_name, hashed_password, credit_balance, status(active/suspended), avatar_url, created_at, updated_at
- **staff_members**: id, email, display_name, hashed_password, role(staff/admin), status(active/suspended), created_at, updated_at
- **personas**: id, staff_id(FK→staff_members), name, age, avatar_url, bio, attributes(JSONB), is_active, created_at, updated_at
- **sessions**: id, user_id(FK→users), persona_id(FK), status(active/closed), created_at, updated_at
  - PARTIAL UNIQUE INDEX: (user_id, persona_id) WHERE status='active' — 同一ユーザー×ペルソナのactiveセッションは1つのみ
- **messages**: id(BIGINT), session_id(FK), sender_type(user/persona), sender_id, title, content, image_url, credit_cost, created_at
  - INDEX: (session_id, id) で差分ポーリング高速化
- **likes**: id, user_id(FK→users), persona_id(FK), created_at
  - UNIQUE: (user_id, persona_id)
- **footprints**: id, user_id(FK→users), persona_id(FK), created_at
  - INDEX: (persona_id, created_at) でスタッフ側の閲覧用
- **notifications**: id, user_id(FK→users), type(enum: system/like/message/credit), title, body, is_read, created_at
- **invitation_tokens**: id, token(String(64), unique, index), email, created_by(FK→staff_members), expires_at, used_at, used_by(FK→users), created_at
- **inquiries**: id, user_id(FK→users), subject, body, status(open/replied/closed), admin_reply, replied_at, created_at
- **templates**: id, staff_id(FK→staff_members), label(例: %OPE01%), content, created_at, updated_at
- **paid_contents**: id, title, description, price, is_active, created_at, updated_at
- **mail_campaigns**: id, type(enum: blast/scheduled/periodic/trigger), subject, body, target_filter(JSONB), scheduled_at, interval, status(draft/scheduled/sent/active), created_at
- **trigger_mail_settings**: id, trigger_event(enum), mail_campaign_id(FK), delay_minutes, is_active, created_at
- **line_bot_accounts**: id, line_bot_id, memo, webhook_url, is_active, subscriber_count, monthly_delivery_count, created_at, updated_at
- **age_verifications**: id, user_id(FK→users), status(enum: pending/approved/rejected), submitted_at, reviewed_at, reviewer_id(FK→staff_members)

### Alembicマイグレーション

| リビジョン | 説明 |
|-----------|------|
| `b0235a46ef8f` | 初期テーブル作成（全15テーブル + セッション部分ユニークインデックス） |
| `a1b2c3d4e5f6` | invitation_tokensテーブル追加 |
| `b2c3d4e5f6a7` | invitation_tokensからpersona_idカラム削除 |
| `d4e5f6a7b8c9` | accountsテーブルをusers + staff_membersに分離、FK参照カラムリネーム |

---

## ネットワーク・プロキシ
- Nginx 2ノード構成（proxy-node-1, proxy-node-2）
- proxy-net / internal-net でネットワーク論理分離
- X-Forwarded-For ヘッダー書き換えでスタッフIP隠匿
- ヘルスチェック付きアップストリーム設定

## レスポンシブ対応（ユーザー側）
- モバイル: BottomNav（5タブ固定ナビ、md:hidden）、Sidebar非表示（hidden md:flex）
- Tailwindブレークポイント: sm(640px), md(768px), lg(1024px)
- 全ページ: p-4 md:p-8、グリッド: grid-cols-2 sm:grid-cols-3 md:grid-cols-4
- AppLayout: pb-16 md:pb-0（ボトムナビ分のスペーシング）
- ポイント購入: モバイルではマイページ内のボタンからアクセス
- ローディング: LoadingSpinnerコンポーネント（teal色スピナー）を全データ取得ページに適用

---

## フロントエンド分離の理由
- スタッフ側のコードがユーザーに配信されない（セキュリティ）
- 独立してデプロイ・スケール可能
- スタッフ側は複雑なUI（複数チャット並行管理等）になるため別アプリの方が開発しやすい

---

## 実装順序
1. docker-compose.yml + 各 Dockerfile ✅
2. FastAPI 基盤（config, database, models） ✅
3. Alembic マイグレーション ✅
4. APIエンドポイント（messages/poll, messages/send, credits） ✅
5. プロキシノード設定 ✅
6. フロントエンド（user → staff の順） ✅
7. QA・バグ修正 ✅
8. 招待メール登録機能 ✅
9. スタッフ用お知らせページ ✅
10. 管理画面にユーザー表示名・ペルソナ名を表示 ✅
11. ユーザー側レスポンシブ対応（モバイル用ボトムナビ） ✅
12. 本番デプロイ設定（Nginx + docker-compose.prod.yml + CORS） ✅
13. accountsテーブル分離（users + staff_members）+ 認証エンドポイント分離 ✅
14. チャットアバター表示 + スタッフ向けユーザー検索開放 ✅
15. UX改善（ローディングスピナー・モバイルポイント購入導線・メッセージ一覧プレビュー） ✅

---

## 実装上の注意事項

- **トレーリングスラッシュ**: FastAPIルーターのパスは `""` で定義（`"/"` だと307リダイレクトが発生）。フロントエンドのAPIパスも末尾スラッシュなしで統一
- **セッション重複防止**: アプリレベル（既存activeセッション返却）+ DBレベル（部分ユニークインデックス）の二重ガード
- **足跡upsert**: 同一ユーザー×ペルソナの足跡は新規作成ではなく日時更新
- **クレジット消費**: ユーザーのメッセージ送信時に1クレジット消費。staff/personaのメッセージは無料
- **Dockerマウント**: `./backend/app` はボリュームマウント（自動リロード）、`./backend/alembic` はビルド時コピー（変更時は `docker compose build api` が必要）
- **招待登録**: ペルソナとの紐付けなし。登録完了時に全staff/adminへ通知。トークンは1回限り使用可、72時間で期限切れ
- **表示名解決**: `get_display_name_map()` / `get_persona_name_map()` でバッチID→名前変換（N+1回避）
- **CORS本番対応**: 環境変数 `ALLOWED_ORIGINS` が設定されていれば固定オリジン許可、なければ localhost パターン許可

---

## 本番デプロイ構成

```
[ユーザー] → [プロキシサーバー (Nginx + SSL)] → [アプリサーバー (Docker)]
                 別マシン（自宅LAN）               別マシン（自宅LAN）
```

- サブドメイン分離: app.example.com(→:3000), staff.example.com(→:3001), api.example.com(→:8080)
- SSL: Let's Encrypt（プロキシサーバー側で終端）
- 設定ファイル: `deploy/nginx/*.conf`, `docker-compose.prod.yml`, `deploy/DEPLOY.md`
- 環境変数: `.env.prod`（SECRET_KEY, POSTGRES_PASSWORD, ドメイン名）
- DB/Redis: 127.0.0.1バインド（外部アクセス不可）
- フロントエンド/API: 0.0.0.0バインド（プロキシサーバーからアクセス可能）

## 未実装機能

- メール送信（DB設計とCRUD APIのみ。送信ライブラリ未導入）
- 決済連携（クレジット購入は仮実装のみ）
