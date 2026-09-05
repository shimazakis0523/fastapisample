# CLAUDE.md

このリポジトリで作業する際の前提。実装原則は `specs/constitution.md` を正とする
(このファイルはその要約 + 操作方法)。

## プロジェクト概要

Spec駆動開発 + ハーネスエンジニアリングを前提としたFastAPIプロジェクトテンプレート。
サンプル機能として商品(Item)のCRUDを実装済み (`specs/001-item-management/`)。
`admin/` に管理フロントエンド (Next.js) を同梱し、Railway (API+DB) / Vercel
(フロントエンド) へのデプロイを想定している (`specs/002-admin-frontend/`)。

## アーキテクチャ

```
app/api/v1/*      … ルーター (HTTPの形を定義するだけ。ビジネスロジックを書かない)
app/services/*    … ビジネスロジック・存在チェック・部分更新のマージ
app/repositories/* … 永続化 (SQLAlchemyクエリはここだけに書く)
app/models/*      … SQLAlchemy ORMモデル
app/schemas/*     … Pydanticの入出力スキーマ
app/core/*        … 設定・ロギング・共通例外
app/db/*          … エンジン/セッションファクトリ
```

依存方向は `api → services → repositories → models` の一方向。詳細な規約は
`specs/constitution.md` を参照。

## Spec駆動開発ワークフロー

新機能は必ず spec → plan → tasks → implement の順で進める。対応するスラッシュ
コマンドが `.claude/commands/` にある。

| コマンド | 役割 |
| --- | --- |
| `/specify <機能概要>` | `specs/<NNN>-<slug>/spec.md` を作成 (要求) |
| `/plan [対象]` | `plan.md` を作成 (技術設計) |
| `/tasks [対象]` | `tasks.md` を作成 (タスク分解) |
| `/implement [対象]` | タスクを順に実装し、都度 lint/typecheck/test で検証 |
| `/verify` | ハーネス全体 (lint/型/テスト/契約テスト) を実行して結果を報告 |

`specs/001-item-management/` が実際に実装済みの worked example。新しい機能を
書く前に一読すると型がわかる。`specs/002-admin-frontend/` は管理フロントエンド
+ デプロイ設定の実装例。

## 管理フロントエンド (admin/)

FastAPI本体とは独立したNext.js (App Router) プロジェクト。`app/`配下のPythonの
ハーネス (ruff/mypy/pytest) の対象外で、`admin/`内で完結する
(`npm run lint` / `npm run build`)。バックエンドへのアクセスはブラウザから直接
行わず、Server Components / Server Actions がサーバー側でFastAPIを呼ぶ
(`admin/lib/api.ts`)。`admin/AGENTS.md`(`admin/CLAUDE.md`から読み込まれる)に
このNext.jsバージョン固有の注意点がある。

## 開発ハーネス

```
make setup      # uv sync + pre-commit install
make run        # 開発サーバ起動 (uvicorn --reload)
make test       # pytest (unit + integration + contract, coverage付き)
make lint       # ruff check + ruff format --check
make fmt        # ruff format + ruff check --fix
make typecheck  # mypy
make check      # lint + typecheck + test (マージ前に必ずgreenにする)
make migrate    # alembic upgrade head
make migration name="..."  # alembic revision --autogenerate
```

- `tests/unit/` … service層 (repositoryは実DBセッション、モックは使わない)
- `tests/integration/` … `httpx.AsyncClient` + ASGITransport でAPI層をend-to-end
- `tests/contract/` … schemathesisでOpenAPIスキーマに対する契約テスト。実プロセス
  として起動したuvicornにHTTPでアクセスする (理由は当該ファイルのコメントを参照)。

## コーディング規約 (詳細は specs/constitution.md)

- 非同期I/Oのみ。ブロッキング呼び出しをリクエストパスに書かない。
- DBの commit/rollback はリクエスト境界 (`get_db_session`) でのみ行う。
- 外部入力由来の整数値は上限を設ける (DBドライバの整数オーバーフロー対策)。
- PATCHで non-nullable なフィールドに `null` を許容しない。
- 新規エンドポイントには unit + integration テストを追加し、`responses=` で
  発生しうる非2xxステータスをOpenAPIスキーマに明記する。

## CI

`.github/workflows/ci.yml`: lint → format check → typecheck → test →
(成功後) Dockerイメージビルド。ローカルの `make check` と同じ内容を実行する。

## デプロイ

Railway (API + Postgres) / Vercel (`admin/`) 構成。手順は README.md の
「デプロイ」を参照。`entrypoint.sh` がコンテナ起動時に `alembic upgrade head`
を実行し、`Settings.database_url` が `postgres(ql)://` 形式を `asyncpg` ドライバ
向けに自動変換する。
