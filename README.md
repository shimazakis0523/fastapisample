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
