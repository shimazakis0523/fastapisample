# fastapisample

Spec駆動開発 + ハーネスエンジニアリングを前提にした FastAPI プロジェクトテンプレート。
Claude Code などのAIコーディングエージェントと人間の双方が、仕様に基づいて安全に
開発を進められることを目的にしている。

## 特徴

- **Spec駆動**: `specs/<NNN>-<slug>/{spec,plan,tasks}.md` の順で仕様→設計→タスクを
  積み上げてから実装する。`.claude/commands/` に `/specify` `/plan` `/tasks`
  `/implement` `/verify` を用意済み。
- **ハーネス**: ruff (lint/format) / mypy / pytest (unit・integration・
  schemathesisによる契約テスト) / pre-commit / GitHub Actions CI / Docker /
  devcontainer 一式。`make check` 一発で全部回せる。
- **worked example**: 商品(Item)のCRUDを、spec駆動フローに沿って実装済み
  (`specs/001-item-management/`)。新機能を書く前の型として参照できる。
- **管理フロントエンド**: `admin/` に Next.js製の管理画面 (一覧/作成/編集/削除) を
  同梱。Railway (API + Postgres) / Vercel (フロントエンド) へのデプロイ手順は
  下記「デプロイ」を参照。

詳しい規約は [`CLAUDE.md`](./CLAUDE.md) と [`specs/constitution.md`](./specs/constitution.md)
を参照。

## セットアップ

```bash
make setup        # uv sync + pre-commit install
cp .env.example .env
make migrate      # DBにテーブルを作成 (alembic upgrade head)
make run          # http://localhost:8000 (docs: /docs, health: /health)
```

デフォルトの `DATABASE_URL` は SQLite (`sqlite+aiosqlite:///./app.db`)。
Postgresでの起動には `docker compose up` を使う。

## よく使うコマンド

```bash
make test        # pytest (coverage付き)
make lint         # ruff check + format --check
make fmt          # ruff format + check --fix
make typecheck     # mypy
make check         # lint + typecheck + test (マージ前に必須)
make migrate                  # alembic upgrade head
make migration name="..."     # alembic revision --autogenerate
```

## ディレクトリ構成

```
app/            # アプリケーション本体 (api/services/repositories/models/schemas/core/db)
tests/          # unit / integration / contract
alembic/        # DBマイグレーション
admin/          # 管理フロントエンド (Next.js, 独立したnpmプロジェクト)
specs/          # spec駆動開発の成果物 (constitution / テンプレート / 各機能のspec)
.claude/commands/  # spec駆動ワークフロー用スラッシュコマンド
```

## 新しい機能を追加する

1. `/specify <機能概要>` で `specs/<NNN>-<slug>/spec.md` を作成
2. `/plan` で技術設計 (`plan.md`) を作成
3. `/tasks` でタスク分解 (`tasks.md`) を作成
4. `/implement` で実装 (タスクごとに lint/typecheck/test)
5. `/verify` で最終確認

手動で進める場合も、この順序と `specs/constitution.md` の原則に従う。

## デプロイ

バックエンド(API + DB)は Railway、管理フロントエンドは Vercel にデプロイする
構成 (詳細は `specs/002-admin-frontend/plan.md`)。

### Railway (API + Postgres)

1. Railwayでプロジェクトを新規作成し、このリポジトリを接続 (root repoのまま、
   `admin/` は含めない設定でよい — `railway.json` がDockerfileビルドを指定)。
2. 同じプロジェクトに Postgres プラグインを追加する。
3. APIサービスの環境変数に、Postgresプラグインが生成する `DATABASE_URL` を
   そのまま設定する (`postgresql://...` 形式のままでよい。アプリ側で
   `postgresql+asyncpg://` に自動変換される)。
4. `CORS_ORIGINS` に、後述のVercelデプロイ後のURLを設定する
   (例: `https://your-admin.vercel.app`)。
5. デプロイ時、コンテナ起動前に `alembic upgrade head` が自動実行される
   (`entrypoint.sh`)。ポートはRailwayが注入する `PORT` を自動的に使う。

### Vercel (管理フロントエンド)

1. Vercelでプロジェクトを新規作成し、このリポジトリを接続。
2. プロジェクト設定の Root Directory を `admin` に変更。
3. 環境変数 `API_BASE_URL` に、Railwayにデプロイしたバックエンドの公開URLを設定
   (ブラウザには公開されないサーバー専用の変数)。
4. デプロイ後、Railway側の `CORS_ORIGINS` にこのVercel URLを追加する。
