# Spec: エンタープライズ認証ブローカー + RBAC (Stage 2)

- ステータス: Draft
- 関連plan: `plan.md`

## 概要

Auth0のEnterprise Connectionを使い、Microsoft Entra ID (Azure AD) を上流IdPとした
ブローカー認証を追加する。あわせてAuth0のRBAC機能を使い、ロールに応じた認可
(操作の許可/拒否) をFastAPI側で実施する。Stage 1 (Auth0単体でのOIDC認証) の土台の
上に、エンタープライズで一般的な「IdP連合 + ロールベースアクセス制御」を練習する。

## ユーザーストーリー

- 組織のユーザーとして、自社のMicrosoft Entra IDアカウントで管理画面にログイン
  したい。
- 管理者として、一般ユーザーには参照・作成・更新のみを許可し、削除は限られた
  ロールのユーザーのみに許可したい。

## 機能要件

- **FR-301**: Auth0テナントに、Microsoft Entra IDをIdPとするEnterprise Connection
  を設定し、既存の管理フロントエンド用Applicationで有効化すること。
- **FR-302**: Auth0は、発行するアクセストークンに、ユーザーのロールに紐づく
  permission一覧を含めること (Auth0のRBAC機能: "Enable RBAC" +
  "Add Permissions in the Access Token" を利用)。
- **FR-303**: FastAPIは、検証済みアクセストークンの`permissions`クレームから
  権限一覧を取得できること。
- **FR-304**: 商品削除 (`DELETE /api/v1/items/{id}`) は、`delete:items` 権限を
  持つユーザーのみ許可すること。権限を持たない認証済みユーザーがリクエストした
  場合、FastAPIは403を返すこと。
- **FR-305**: 商品の参照・作成・更新 (`GET`/`POST`/`PATCH`) は、Stage 1と同様に
  認証済みであれば全ユーザーに許可すること (ロール不問、既存の後方互換)。
- **FR-306**: 管理フロントエンドは、削除操作がAPI側で403 (権限不足) を返した場合、
  汎用エラー画面に落ちずにユーザーへメッセージを表示すること。
- **FR-307**: 管理フロントエンドの未ログイン時のトップページに、通常ログインと
  Entra ID経由のログイン (Enterprise Connection) をそれぞれ選択できる、視認性の
  高いボタンを設けること。Connection名は環境変数で設定可能とし、未設定の場合は
  Entra ID用ボタンを表示しないこと (Stage 1の通常ログインのみになる)。

## 非機能要件

- Stage 1で構築したAuth0のDB Connection (通常のユーザー名/パスワードログイン) は、
  Enterprise Connection導入後も引き続き動作すること (既存ユーザーへの影響なし)。

## スコープ外

- Entra ID側のグループとAuth0ロールの自動同期 (初期のロール割当はAuth0ダッシュ
  ボードでの手動操作とする)。
- `delete:items` 以外の細粒度なPermission設計 (read/write個別権限化等)。
- Entra ID以外の追加Enterprise Connection。
- Entra IDテナント自体の新規作成 (既存のAzureサブスクリプション/テナントを前提)。

## 未解決事項

- 無し。Enterprise Connectionの作成とRoleの割当はAuth0/Azureダッシュボードでの
  手動設定 (ユーザー側作業) として進める。
