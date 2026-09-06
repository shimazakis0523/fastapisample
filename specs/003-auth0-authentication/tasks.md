# Tasks: Auth0認証 (Stage 1)

- 対応plan: `plan.md`

- [x] 設定: `auth0_domain` / `auth0_audience` を`Settings`に追加 (対応: FR-204)
- [x] バックエンド: `app/core/auth.py` (JWT検証依存性) を実装 (対応: FR-204, FR-205)
- [x] バックエンド: `/api/v1/items`の全エンドポイントに認証依存性を適用 (対応: FR-204)
- [x] バックエンド: 401レスポンスをOpenAPIスキーマに明記
- [x] 単体テスト: JWT検証ロジック (署名不正/audience不一致/期限切れ)
- [x] 統合テスト: 認証ヘッダー無しリクエストが401になることを確認
- [x] フロントエンド: `admin/lib/auth0.ts` (Auth0Client) を追加
- [x] フロントエンド: `admin/proxy.ts` を追加 (対応: FR-201, FR-202)
- [x] フロントエンド: `admin/lib/api.ts` を`createFetcher`ベースに変更 (対応: FR-203)
- [x] フロントエンド: 未ログイン時のログイン導線、ログイン後のログアウト導線を追加
- [x] ドキュメント: README.mdにAuth0環境変数の設定手順を追加
- [ ] 手動確認: 実際のAuth0テナントでログイン〜CRUD操作のE2E確認 (Auth0側の設定待ち)
