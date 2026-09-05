---
description: ハーネス全体(lint/型/テスト/契約テスト)を実行して結果を報告する
---

プロジェクトの品質ゲートを一通り実行し、結果を要約してください。

実行するコマンド:

1. `uv run ruff check .`
2. `uv run ruff format --check .`
3. `uv run mypy app tests`
4. `uv run pytest`
5. 起動確認が必要な場合は `uv run uvicorn app.main:app` を一時起動し `/health` と
   `/openapi.json` を確認後に停止する。

いずれかが失敗した場合は原因を修正して再実行し、すべて成功するまで繰り返す。
最終的に成功/失敗の一覧を報告する。
