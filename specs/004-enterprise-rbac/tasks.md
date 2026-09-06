# Tasks: エンタープライズ認証ブローカー + RBAC (Stage 2)

- 対応plan: `plan.md`

- [x] バックエンド: `app/core/auth.py`に`require_permission`依存性ファクトリを追加 (対応: FR-303)
- [x] バックエンド: `DELETE /api/v1/items/{id}`に`require_permission("delete:items")`を適用し、403をresponsesに明記 (対応: FR-304)
- [x] テスト用フィクスチャ: `client`に`delete:items`権限を付与し、権限無しケース用のフィクスチャを追加 (対応: FR-304)
- [x] フロントエンド: `admin/lib/api.ts`に`ForbiddenError`を追加 (対応: FR-306)
- [x] フロントエンド: `admin/app/actions.ts`の`deleteItemAction`で403を捕捉し`/?error=forbidden`へリダイレクト (対応: FR-306)
- [x] フロントエンド: `admin/app/page.tsx`で`error=forbidden`時にメッセージを表示 (対応: FR-306)
- [x] 単体テスト: `require_permission`の権限あり/なし/クレーム欠如のケース (対応: FR-304)
- [x] 統合テスト: `delete:items`権限を持たないトークンでのDELETEが403になることを確認 (対応: FR-304)
- [x] ドキュメント: README.mdにEnterprise Connection/RBAC設定手順を追加 (対応: FR-301, FR-302)
- [ ] 手動確認: Entra IDアカウントでのログイン、ロール別の削除可否のE2E確認 (Auth0/Azure側の設定待ち)
