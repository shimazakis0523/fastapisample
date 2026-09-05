---
description: tasks.md のタスクを順に実装し、都度検証する
argument-hint: "[対象spec番号 (省略時は最新)]"
---

対象の tasks.md に従って実装を進めてください。

対象: $ARGUMENTS (省略時は `specs/` 内で最も番号が大きいディレクトリ)

手順:

1. 対象の `specs/<NNN>-<slug>/tasks.md` を読み、未完了 (`- [ ]`) のタスクを
   先頭から確認する。
2. タスクを1つずつ実装する。各タスク完了ごとに:
   - `make lint` `make typecheck` を実行し、問題があれば修正する。
   - 関連するテストを `make test` (または対象ファイルのみ
     `uv run pytest <path>`) で実行し、パスを確認する。
   - 該当タスクを `- [x]` に更新する。
3. 全タスク完了後、`make check` (lint + typecheck + test 一式) を実行し、
   すべて green であることを確認する。
4. `specs/<NNN>-<slug>/spec.md` の各機能要件が満たされているか一つずつ確認し、
   満たしていない場合は理由を報告する。
5. 完了したら変更点の要約と `make check` の結果を報告する。仕様に無い機能を
   追加しない。
