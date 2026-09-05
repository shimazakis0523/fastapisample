# Tasks: 商品(Item)管理

- 対応plan: `plan.md`

- [x] モデル: `Item` SQLAlchemyモデルを追加 (対応: FR-001〜FR-006)
- [x] マイグレーション: `items` テーブル作成 (autogenerate)
- [x] リポジトリ: `ItemRepository` (get/list/create/delete)
- [x] スキーマ: `ItemCreate` / `ItemUpdate` / `ItemRead`
      (`name`/`price` への明示的null拒否、タイムゾーン補正を含む) (対応: FR-001, FR-005)
- [x] サービス: `ItemService` (存在チェック・部分更新マージ) (対応: FR-002, FR-004)
- [x] API: `/api/v1/items` の5エンドポイント (ページング上限・404/400ドキュメント化
      を含む) (対応: FR-001〜FR-006)
- [x] 単体テスト: `tests/unit/test_item_service.py`
- [x] 統合テスト: `tests/integration/test_items_api.py`
- [x] 契約テスト: `tests/contract/test_openapi_contract.py`
- [x] ドキュメント更新: 本spec一式・CLAUDE.md・README.md
