# Tasks: 管理フロントエンド + デプロイ

- 対応plan: `plan.md`

- [x] 設定: `cors_origins` 追加、`database_url` 正規化バリデータ追加 (対応: FR-105, FR-106)
- [x] API: `app/main.py` に `CORSMiddleware` を追加 (対応: FR-105)
- [x] デプロイ: `entrypoint.sh` 追加、Dockerfileを `$PORT` 対応に変更 (対応: FR-107, FR-108)
- [x] デプロイ: `railway.json` 追加
- [x] 単体テスト: `database_url` 正規化のテストを追加
- [x] フロントエンド: `admin/` に Next.js (TypeScript, App Router) を作成
- [x] フロントエンド: `lib/api.ts` (fetchラッパー) (対応: FR-101〜104)
- [x] フロントエンド: 一覧ページ (対応: FR-101)
- [x] フロントエンド: 新規作成ページ + Server Action (対応: FR-102)
- [x] フロントエンド: 編集ページ + Server Action (対応: FR-103)
- [x] フロントエンド: 削除 Server Action (対応: FR-104)
- [x] 検証: バックエンド `make check` / フロントエンド `lint`+`build` / Playwrightでの
      ブラウザ動作確認
- [x] ドキュメント更新: README.md にRailway/Vercelデプロイ手順を追加
