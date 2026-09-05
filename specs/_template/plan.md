# Plan: <機能名>

- 対応spec: `spec.md`

## アーキテクチャ概要

新規・変更するモジュールを、`api (router) → services → repositories → models` の
層構造に沿って列挙する。

- `app/models/...`:
- `app/schemas/...`:
- `app/repositories/...`:
- `app/services/...`:
- `app/api/...`:

## データモデル

変更・追加するテーブル/カラム/制約。マイグレーションが必要な場合はその旨を記載する。

| カラム | 型 | 制約 | 備考 |
| --- | --- | --- | --- |
|  |  |  |  |

## APIコントラクト

| メソッド | パス | リクエスト | レスポンス | 対応する機能要件 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## エラーハンドリング

発生しうる異常系(存在しないリソース、競合、バリデーションエラー等)と、対応する
HTTPステータス・レスポンス形を記載する。

## テスト戦略

- Unit (service層):
- Integration (API層):
- Contract (schemathesis): 既存の `tests/contract/test_openapi_contract.py` が
  新規エンドポイントも自動的にカバーする。追加の考慮点があれば記載。

## 要件対応表

spec.md の各機能要件IDが、この plan のどこで実現されるかを対応付ける。

| 要件ID | 対応箇所 |
| --- | --- |
| FR-001 |  |
