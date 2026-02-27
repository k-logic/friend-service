# CLAUDE.md - Friend プロジェクト

## プロジェクト概要
多拠点型コンシェルジュチャットプラットフォーム（FastAPI + Next.js + PostgreSQL + Redis）

## コミュニケーション
- 日本語で対応すること
- コミットメッセージも日本語で書く

## 開発ルール
- アーキテクチャの決定事項や認識合わせの結果はメモリ（memory/）に保存する
- 実装前にPLAN.mdの該当ステップを確認し、計画に沿って進める
- 大きな設計変更がある場合は実装前に確認を取る

## 技術スタック
- バックエンド: FastAPI / PostgreSQL / Redis / Alembic
- フロントエンド: Next.js（ユーザー側・オペレーション側の2アプリ構成）
- インフラ: Docker Compose / Nginx プロキシ
- 本番: Nginxプロキシサーバー（別マシン）+ Dockerアプリサーバー（自宅LAN内2台構成）

## DB設計
- users テーブル（顧客）と staff_members テーブル（運営者）は分離済み
- 認証: JWTに `type` フィールド（user / staff）を含む
- ユーザー認証: `/api/v1/auth/*`、スタッフ認証: `/api/v1/staff/auth/*`
- 権限: `get_current_user` / `get_current_staff` / `get_current_admin` の3段階

## コマンド
- 開発起動: `docker compose up -d`
- バックエンドのみ: `docker compose up api db redis -d`
- マイグレーション: `docker compose exec api alembic upgrade head`
- シードデータ: `docker compose exec api python -m scripts.seed`
- 本番起動: `docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build`

## 禁止事項
- 本番環境への直接操作
- シークレット情報のコミット（.env, .env.prod等）
