# Plan: 商品(Item)管理

- 対応spec: `spec.md`

## アーキテクチャ概要

- `app/models/item.py`: `Item` (SQLAlchemyモデル)
- `app/schemas/item.py`: `ItemCreate` / `ItemUpdate` / `ItemRead` (Pydanticスキーマ)
- `app/repositories/item.py`: `ItemRepository` (get/list/create/delete、部分更新は
  サービス層で属性を書き換えてから repository を介さず flush される)
- `app/services/item.py`: `ItemService` (存在チェック・`ItemNotFoundError` 送出・
  部分更新のマージ)
- `app/api/v1/items.py`: `/api/v1/items` 配下の5エンドポイント
- `app/api/deps.py`: `ItemServiceDep` (DBセッション→リポジトリ→サービスの組み立て)

## データモデル

| カラム | 型 | 制約 | 備考 |
| --- | --- | --- | --- |
| id | Integer | PK |  |
| name | String(200) | NOT NULL, index |  |
| description | Text | NULL可 |  |
| price | Float | NOT NULL, `ge=0` はAPI層で検証 |  |
| created_at | DateTime(timezone=True) | NOT NULL, server_default=now() |  |
| updated_at | DateTime(timezone=True) | NOT NULL, onupdate=now() |  |

マイグレーション: `alembic/versions/e182f231a228_create_items_table.py`。

## APIコントラクト

| メソッド | パス | リクエスト | レスポンス | 対応する機能要件 |
| --- | --- | --- | --- | --- |
| POST | /api/v1/items | ItemCreate | 201 ItemRead / 400 / 422 | FR-001 |
| GET | /api/v1/items | limit, offset (query) | 200 ItemRead[] | FR-003 |
| GET | /api/v1/items/{item_id} | - | 200 ItemRead / 404 | FR-002 |
| PATCH | /api/v1/items/{item_id} | ItemUpdate | 200 ItemRead / 404 / 400 / 422 | FR-004, FR-005 |
| DELETE | /api/v1/items/{item_id} | - | 204 / 404 | FR-006 |

`item_id` / `offset` は `_INT32_MAX` (2,147,483,647) を上限とし、DBドライバの
整数オーバーフローを未然に防ぐ。400 はStarletteが不正なJSON本文を拒否した場合。

## エラーハンドリング

- 存在しないIDへのアクセスは `ItemNotFoundError` を送出し、
  `app/main.py` の例外ハンドラで 404 に変換する。
- `name` / `price` への明示的な `null` は、`ItemUpdate` のフィールド型を
  `float | None` にせず、`exclude_unset` でしか「未指定」を表現しない設計にする
  ことでスキーマレベルで拒否する (`app/schemas/item.py` 参照)。

## テスト戦略

- Unit: `tests/unit/test_item_service.py` (作成・取得・更新・削除・一覧、
  存在しないIDでの例外)
- Integration: `tests/integration/test_items_api.py` (HTTP経由の一連のCRUD、
  バリデーションエラー)
- Contract: `tests/contract/test_openapi_contract.py` (schemathesisで全エンドポイ
  ントをファジング。`allow_header_conformance` / `negative_data_rejection` は
  意図的な理由により除外)

## 要件対応表

| 要件ID | 対応箇所 |
| --- | --- |
| FR-001 | `create_item` (api/service/repository) |
| FR-002 | `get_item` |
| FR-003 | `list_items` |
| FR-004 | `update_item` |
| FR-005 | `ItemUpdate` のフィールド設計 |
| FR-006 | `delete_item` |
