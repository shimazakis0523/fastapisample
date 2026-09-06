# Plan: エンタープライズ認証ブローカー + RBAC (Stage 2)

- 対応spec: `spec.md`

## アーキテクチャ概要

```
Microsoft Entra ID (上流IdP)
   ↕ OIDC federation
Auth0 (Enterprise Connection: "Microsoft Entra ID")
   ↕ 通常のOIDC (Stage 1と同じ)
Next.js (@auth0/nextjs-auth0) → FastAPI (Bearer token)
```

Auth0からみるとEntra IDはDB Connectionと並列の1つのConnectionであり、
Next.js/FastAPI側の認証フロー自体はStage 1から変更しない。ユーザーがAuth0の
Universal Loginでメールアドレスを入力すると、Home Realm Discoveryによりドメイン
に応じてEntra IDへリダイレクトされる (Auth0標準機能、追加コード不要)。

認可 (RBAC) は、Auth0の "Enable RBAC" + "Add Permissions in the Access Token" を
有効化し、アクセストークンの`permissions`クレームにpermission文字列の配列を含める。
FastAPI側はこのクレームを見て許可/403を判定する。

- `app/models/...`: 変更なし
- `app/schemas/...`: 変更なし
- `app/repositories/...`: 変更なし
- `app/services/...`: 変更なし
- `app/core/auth.py`: `permissions`クレームを見る`require_permission(permission)`
  依存性ファクトリを追加
- `app/api/v1/items.py`: DELETEエンドポイントにのみ
  `Depends(require_permission("delete:items"))` を追加
- `admin/lib/api.ts`: 403を判別できる`ForbiddenError`を追加
- `admin/app/actions.ts` / `admin/app/page.tsx`: 403を捕捉してユーザーへ表示
- `admin/app/page.tsx`: `requireSession()`によるハードリダイレクトをやめ、
  未ログイン時は自身で「Log in」「Log in with Entra ID」の2つのボタンを表示
  するように変更 (リダイレクトすると、これらのボタンが表示される前に遷移して
  しまうため)。`AUTH0_ENTERPRISE_CONNECTION`が未設定ならEntra ID用ボタンは
  表示しない。
- `admin/app/layout.tsx`: ヘッダーはログイン済み (email + Log out) の場合のみ
  表示する (未ログイン時のログイン導線は上記の通りページ本体側に統一)。
- `docs/auth-implementation-guide.md` (新規): Stage 1/Stage 2で実施した手順を
  まとめた実装ガイド。`admin/app/page.tsx`の未ログイン画面からリンクする。

## Auth0/Azureダッシュボード設定 (ユーザー側の手動作業)

1. Azure Portal: Entra ID > アプリの登録 で新規App registrationを作成する。
   - リダイレクトURI: `https://<AUTH0_DOMAIN>/login/callback`
   - クライアントシークレットを発行
   - APIのアクセス許可: `openid` `profile` `email` (Microsoft Graph)
2. Auth0 Dashboard: Authentication > Enterprise > Microsoft Entra ID (Azure AD)
   で新規Connectionを作成し、上記のTenant ID/Client ID/Client Secretを設定する。
   既存の管理フロントエンド用ApplicationでこのConnectionを有効化する。
3. Auth0 Dashboard: APIs > (既存の `fastapisample-api`) > RBAC Settings で
   "Enable RBAC" と "Add Permissions in the Access Token" をONにする。
   Permissions タブで `delete:items` を追加する。
4. Auth0 Dashboard: User Management > Roles で `admin` ロールを作成し、
   `delete:items` permissionを割り当てる。削除を許可したいユーザーにこのロールを
   手動で割り当てる。

## バックエンド変更

- `app/core/auth.py`:
  - `require_permission(permission: str)`: `verify_token`の結果 (`CurrentUser`)
    の`permissions`クレーム (無ければ空リスト) を見て、`permission`が含まれて
    いなければ403 (`HTTPException`) を送出する依存性ファクトリを追加する。
- `app/api/v1/items.py`:
  - `delete_item`に`dependencies=[Depends(require_permission("delete:items"))]`
    を追加する。
  - 403を`responses=`に明記する。

## フロントエンド変更 (admin/)

- `admin/lib/api.ts`: `request()`が403を受けた場合、通常の`Error`ではなく
  `ForbiddenError`を投げるようにする。
- `admin/app/actions.ts`: `deleteItemAction`で`ForbiddenError`を捕捉し、
  `/?error=forbidden`にリダイレクトする (他のエラーは従来通り再送出)。
- `admin/app/page.tsx`: `searchParams`の`error=forbidden`を見て、削除失敗を
  伝えるメッセージを一覧画面に表示する。

## 環境変数

フロントエンド (`admin/.env.local` / Vercel) に `AUTH0_ENTERPRISE_CONNECTION`
(Auth0で作成したEnterprise ConnectionのConnection名) を追加する。未設定なら
Entra IDログインリンクを表示しない (Stage 1の通常ログインのみ動作する後方互換)。

## エラーハンドリング

- 権限不足での削除: FastAPIは403。フロントエンドは汎用エラー画面に落とさず、
  一覧画面上に「削除の権限がありません」旨のメッセージを表示する。

## テスト戦略

- Unit: `require_permission`の検証ロジック (permissionあり/なし/クレーム自体
  無しの各ケース)。
- Integration: `delete:items`権限を持たないトークンでのDELETEが403になることを
  確認するテストを追加する。既存の`client`フィクスチャは`delete:items`を含む
  permissionsを持つものとして扱い (既存テストの後方互換のため)、権限を持たない
  ケース専用のフィクスチャを別途追加する。
- 手動: Auth0の実テナントでEntra ID Connection設定後、Entra IDアカウントでの
  ログイン〜ロール別の削除可否をE2E確認する (ユーザー側でAzure/Auth0設定後)。

## 要件対応表

| 要件ID | 対応箇所 |
| --- | --- |
| FR-301 | Auth0/Azureダッシュボード設定 (手動) |
| FR-302 | Auth0 RBAC設定 (手動) |
| FR-303, FR-304 | app/core/auth.py, app/api/v1/items.py |
| FR-305 | 既存の`verify_token`のみを使うエンドポイント (変更なし) |
| FR-306 | admin/lib/api.ts, admin/app/actions.ts, admin/app/page.tsx |
| FR-307 | admin/app/page.tsx |
| FR-308 | admin/app/page.tsx, docs/auth-implementation-guide.md |
