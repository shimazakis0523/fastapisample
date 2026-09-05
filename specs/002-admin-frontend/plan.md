# Plan: 管理フロントエンド + デプロイ

- 対応spec: `spec.md`

## アーキテクチャ概要

```
admin/ (Next.js, App Router, TypeScript)   … Vercelにデプロイ
  ├─ app/page.tsx              一覧 (Server Component, no-store fetch)
  ├─ app/items/new/page.tsx    新規作成フォーム
  ├─ app/items/[id]/edit/page.tsx  編集フォーム
  ├─ app/actions.ts            Server Actions (create/update/delete、"use server")
  └─ lib/api.ts                 FastAPIを叩くfetchラッパー (API_BASE_URL)

app/ (FastAPI, 既存)                        … Railwayにデプロイ
  ├─ core/config.py    + cors_origins設定、DB URL正規化バリデータ
  └─ main.py           + CORSMiddleware

Postgres (Railway管理)                       … Railwayにデプロイ
```

Next.jsはブラウザから直接FastAPIを叩かず、Server Component/Server Actionsが
サーバー側でFastAPIを呼ぶ(APIのURLをブラウザに露出させない)。書き込み系の
Server Actionは完了後に `revalidatePath`/`redirect` で一覧を更新する。

## バックエンド変更

- `app/core/config.py`:
  - `cors_origins: str` (カンマ区切り、既定 `http://localhost:3000`) を追加。
  - `database_url` に `mode="before"` の field_validator を追加し、
    `postgres://` / `postgresql://` (asyncpgドライバ指定なし) を
    `postgresql+asyncpg://` に書き換える。sqlite等はそのまま通す。
- `app/main.py`: `CORSMiddleware` を追加、`settings.cors_origins` をカンマ分割
  して `allow_origins` に渡す。
- `entrypoint.sh` (新規): `alembic upgrade head && exec uvicorn ...`。
  `Dockerfile` の `CMD` をこれに差し替え、`--port` は `${PORT:-8000}` を使う
  (Railway が動的にポートを割り当てるため)。
- `railway.json` (新規): Dockerfileビルドである旨と `/health` のヘルスチェック
  パスを明示。

## フロントエンド (admin/)

`create-next-app` で新規作成 (TypeScript, App Router, Tailwindなし、素のCSS)。
主要ファイルは上記アーキテクチャ図の通り。データ型 (`Item`) はバックエンドの
`ItemRead` スキーマに対応する最小限のTypeScript interfaceとして手書きする
(OpenAPIからの自動生成は導入しない: スコープに対してオーバーエンジニアリング)。

環境変数: `API_BASE_URL` (サーバー側のみ、`NEXT_PUBLIC_` 不要)。

## デプロイ

- **Railway** (バックエンド + DB): 同一Railwayプロジェクトに「Postgres」プラグ
  インを追加し、生成される `DATABASE_URL` をFastAPIサービスの環境変数として
  設定する (前述のURL正規化により `postgresql://` のままでよい)。
- **Vercel** (フロントエンド): リポジトリを接続し、プロジェクト設定で
  Root Directoryを `admin` に指定。環境変数 `API_BASE_URL` にRailwayの
  バックエンドURLを設定。
- 具体的な手順は `README.md` に記載する。

## エラーハンドリング

- Server Actionsはバックエンドが非2xxを返した場合に例外を送出し、Next.jsの
  既定のエラー画面に委ねる (フォームごとの詳細なエラー表示はスコープ外)。

## テスト戦略

- バックエンド: 既存の `make check` がそのまま通ることを確認 (新規ロジックの
  ユニットテストは `Settings` のURL正規化のみ追加)。
- フロントエンド: `npm run lint` / `npm run build` で静的に確認。
- 手動/E2E: バックエンドとフロントエンドを両方起動し、Playwrightで一覧表示→
  作成→編集→削除のゴールデンパスをブラウザ上で確認する (自動テストとしては
  リポジトリに残さず、実装時の確認のみ)。

## 要件対応表

| 要件ID | 対応箇所 |
| --- | --- |
| FR-101〜104 | `admin/app/*` |
| FR-105 | `app/main.py` の `CORSMiddleware` |
| FR-106 | `app/core/config.py` の validator |
| FR-107 | `entrypoint.sh` |
| FR-108 | `entrypoint.sh` / `Dockerfile` |
