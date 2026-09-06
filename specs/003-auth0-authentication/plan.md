# Plan: Auth0認証 (Stage 1)

- 対応spec: `spec.md`

## アーキテクチャ概要

```
ブラウザ → Next.js (@auth0/nextjs-auth0 v4, proxy.ts でログイン状態を管理)
Next.js → FastAPI (Auth0発行のアクセストークンをBearerヘッダーで送信)
FastAPI → Auth0のJWKSエンドポイントで署名検証 (PyJWT + PyJWKClient)
```

`@auth0/nextjs-auth0` v4は`/auth/login` `/auth/logout` `/auth/callback`等の
ルートを自動でマウントする(手動でルートハンドラを書く必要はない)。Next.js 16
では`middleware.ts`ではなく`proxy.ts`がこの役割を担う。

## バックエンド変更

- `app/core/config.py`: `auth0_domain: str` / `auth0_audience: str` を追加。
- `app/core/auth.py` (新規): `HTTPBearer` + `PyJWKClient`でJWTを検証する
  `verify_token` 依存性を実装。`CurrentUser = Annotated[dict, Depends(verify_token)]`
  として公開する。
- `app/api/v1/items.py`: 各エンドポイントに `CurrentUser` 依存性を追加し、
  未認証リクエストを401で拒否する。
- 依存追加: `PyJWT[crypto]`。

## フロントエンド変更 (admin/)

- `admin/lib/auth0.ts` (新規): `Auth0Client`のインスタンス化。
  `authorizationParameters.audience`にFastAPIのAPI識別子を設定し、Auth0が
  そのaudience向けのアクセストークンを発行するようにする。
- `admin/proxy.ts` (新規): 認証ルートのマウント (Next.js 16の規約)。
- `admin/lib/api.ts`: 素の`fetch`を`auth0.createFetcher(undefined, { baseUrl })`
  + `fetcher.fetchWithAuth()`に置き換え、アクセストークンを自動付与する。
- 各ページ (`page.tsx` 等): `auth0.getSession()`が`null`ならログインへの導線を
  表示する(未ログイン時はAPI呼び出し自体を行わない)。
- ログイン/ログアウトのリンク (`/auth/login` `/auth/logout`) をレイアウトに追加。

## 環境変数

バックエンド (Railway):
- `AUTH0_DOMAIN` / `AUTH0_AUDIENCE`

フロントエンド (Vercel / ローカル `.env.local`):
- `AUTH0_DOMAIN` / `AUTH0_CLIENT_ID` / `AUTH0_CLIENT_SECRET` / `AUTH0_SECRET`
  (`openssl rand -hex 32`で生成) / `AUTH0_AUDIENCE`

## エラーハンドリング

- トークン無し/検証失敗: FastAPIは401 (`WWW-Authenticate: Bearer`)。
- Next.js側で未ログイン: ページ側で`/auth/login`への導線を出す(APIを叩く前に
  弾く。無駄なAPI呼び出しをしない)。

## テスト戦略

- Unit: `verify_token`の検証ロジック(署名不正・audience不一致・期限切れの
  各ケースをモックJWKSで検証)。
- Integration: 既存の `tests/integration/test_items_api.py` に、Authorization
  ヘッダー無しのリクエストが401になることを確認するテストを追加。
- 契約テスト: schemathesisは認証ヘッダーを持たないため、既存の
  `tests/contract/test_openapi_contract.py` は401ドキュメント化への対応が
  必要 (`responses=` に401を追加)。
- 手動: Auth0の実テナントを使ったログイン〜API呼び出しのE2E確認 (ユーザー側で
  Auth0テナント作成後)。

## 要件対応表

| 要件ID | 対応箇所 |
| --- | --- |
| FR-201, FR-202 | admin/proxy.ts, ログイン/ログアウトUI |
| FR-203 | admin/lib/api.ts (createFetcher) |
| FR-204, FR-205 | app/core/auth.py, app/api/v1/items.py |
