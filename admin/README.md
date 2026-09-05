# admin

fastapisample の商品(Item)を操作する管理フロントエンド (Next.js, App Router)。
ブラウザからは直接FastAPIを叩かず、Server Components / Server Actions がサーバー
側で `API_BASE_URL` の FastAPI を呼び出す (`lib/api.ts`)。

## セットアップ

```bash
npm install
cp .env.example .env.local   # API_BASE_URL を実行中のFastAPIに合わせる
npm run dev                  # http://localhost:3000
```

バックエンド (`../`) を先に `make run` などで起動しておくこと。

## コマンド

```bash
npm run dev     # 開発サーバ
npm run build   # 本番ビルド (型チェックも実行される)
npm run lint    # eslint
```

## デプロイ

Vercelにこのリポジトリを接続し、プロジェクト設定の Root Directory を `admin`
に、環境変数 `API_BASE_URL` にRailway等にデプロイしたバックエンドのURLを設定
する。詳細はリポジトリルートの `README.md` 「デプロイ」節を参照。

## Next.jsのバージョンについて

`AGENTS.md` (このディレクトリの `CLAUDE.md` から読み込まれる) を参照。学習データ
にある知識と異なる可能性がある破壊的変更について注記している。
