# プロジェクト憲章 (Constitution)

このプロジェクトにおける全ての spec・plan・実装が従うべき、変更頻度の低い原則。
`/specify` `/plan` `/implement` は必ずこの文書を読んでから作業すること。

## 1. Spec駆動

- 実装に着手する前に、必ず `specs/<NNN>-<slug>/spec.md` (要求) → `plan.md` (設計) →
  `tasks.md` (タスク分解) の順で作成する。順序を飛ばさない。
- 機能要件には一意なID (`FR-001` 等) を振り、plan.md・tasks.md・テストコードから
  遡って参照できるようにする。
- spec に無い機能を実装しない。実装中に spec の不備に気づいた場合は、先に spec を
  修正してから実装を続ける。

## 2. アーキテクチャ

- 層は `api (router) → services → repositories → models` の一方向のみ。
  router から repository・model への直接アクセス、service を跨いだ層の省略は禁止。
- リクエスト/レスポンスの形は `schemas/` (Pydantic) で、永続化の形は `models/`
  (SQLAlchemy) で表現し、混同しない。
- DBセッションのコミット/ロールバックは `db/session.py` の `get_db_session` (リクエスト
  境界) でのみ行う。service/repository は `flush` までに留める。

## 3. APIコントラクト

- 公開APIの形は FastAPI が生成する OpenAPI スキーマそのものが正とする。
- 実装がスキーマと乖離していないかを `tests/contract/test_openapi_contract.py`
  (schemathesis) で検証する。新しいステータスコードを返すようになったら、
  `responses=` で明示的にドキュメント化する。
- 部分更新 (PATCH) では、ドメイン上 non-nullable なフィールドに明示的な `null` を
  許容しない (詳細は `app/schemas/item.py` の `ItemUpdate` を参照)。

## 4. 非同期・データベース

- I/O はすべて非同期。同期的にブロッキングする呼び出しをリクエストパスに書かない
  (`ruff` の `ASYNC` ルールで機械的に検出する)。
- 外部入力に由来する整数値 (path/query パラメータ等) は DB カラム幅を超えないよう
  上限を設ける (`app/api/v1/items.py` の `_INT32_MAX` を参照)。

## 5. テスト

- 新しいエンドポイント・分岐には、最低 1つの unit テスト (service層) と
  1つの integration テスト (API層) を追加する。
- `make check` (ruff check/format + mypy + pytest) が green でない変更はマージしない。
- contract テストが失敗した場合、原則としてスキーマを合わせて修正する。チェックを
  除外するのは、フレームワーク側の制約や意図的な設計判断であることが説明できる
  場合に限る (除外理由は必ずコードコメントに残す)。

## 6. 変更の粒度

- 1つの spec は 1つの凝集した機能に対応させる。無関係な変更を同じ spec に混ぜない。
- タスクは 1〜数ファイル程度の粒度に分解し、各タスクの完了ごとに lint/typecheck/test
  を回せるようにする。
