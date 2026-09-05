---
description: spec.md を元に技術設計(plan.md)を作成する
argument-hint: "[対象spec番号 (省略時は最新)]"
---

指定された仕様から技術設計書を作成してください。

対象: $ARGUMENTS (省略時は `specs/` 内で最も番号が大きいディレクトリ)

手順:

1. 対象の `specs/<NNN>-<slug>/spec.md` と `specs/constitution.md` を読む。
2. 既存コードベース (`app/` 以下) の構造を確認し、既存の層構造
   (router → service → repository → model) に沿う形で設計する。
3. `specs/_template/plan.md` を `specs/<NNN>-<slug>/plan.md` としてコピーし、
   以下を記述する:
   - アーキテクチャ概要 (新規/変更するモジュール)
   - データモデル (テーブル・カラム・制約)
   - APIコントラクト (エンドポイント、リクエスト/レスポンススキーマ)
   - エラーハンドリング方針
   - テスト戦略 (unit/integration/contract)
4. spec.md の各機能要件IDが plan.md のどこで対応されるか対応関係を明記する。
5. 完了したらファイルパスと設計の要点を報告する。まだタスク分解や実装には
   着手しない。
