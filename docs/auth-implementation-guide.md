# Next.js + FastAPI + Auth0 + Entra ID 認証認可 実装ガイド

このリポジトリで実際に実装した手順をまとめたものです。Auth0をOIDCの認可サーバー
として使い (Stage 1)、さらにMicrosoft Entra ID (Azure AD) をEnterprise Connection
経由でブローカーし、ロールベースの認可を追加する (Stage 2) までの流れを説明します。

> **注意**: 本ガイドに出てくる具体的な値 (ドメイン名・API識別子・Connection名・
> ロール名・permission文字列など) はすべて一例です。実際に構築する際にこの通りに
> する必要はありません。値を変える場合は、対応する環境変数と各ダッシュボードの
> 設定を同じ値に揃えてください。
>
> また、バックエンドのホスティング先 (例: Railway, 任意のPaaS/コンテナ基盤) は
> 本ガイドでは特定しません。HTTPSでアクセスでき、コンテナまたはASGIアプリを実行
> できて、環境変数を設定できるプラットフォームであれば構いません。フロントエンド
> (Next.js) のホスティング先も同様にVercel以外で構いません。

## アーキテクチャ概要

```
ブラウザ
  → Next.js管理画面 (@auth0/nextjs-auth0)  … ログイン状態の管理
      → Auth0 (認可サーバー)               … OIDCログイン、JWT発行
          → Microsoft Entra ID              … Stage 2: Enterprise Connection経由の上流IdP
      → FastAPI (Resource Server)          … Auth0発行のアクセストークン(JWT)を検証
```

FastAPI自身はAuth0ともEntra IDとも直接通信しない。FastAPIが信頼するのは
「Auth0が発行し、Auth0のJWKSで検証できる署名付きJWT」だけであり、その裏で
ユーザーがどの手段 (Auth0のユーザー名/パスワード、Google、Entra IDなど) で
ログインしたかは関知しない。

## Stage 1: Auth0によるOIDC認証 (FastAPIをResource Server化する)

### 1. Auth0テナントの準備

1. Auth0にサインアップし、テナントを作成する (例: `dev-xxxxxxxx.us.auth0.com`)。
2. **Applications → APIs → Create API** でバックエンド用のAPIを作成する。
   - Identifier: 任意のURI形式の文字列 (例: `https://my-api`)。**作成後は
     変更できない**ため、タイプミスに注意する。
   - Signing Algorithm: RS256 (デフォルトのままでよい)。
3. **Applications → Applications → Create Application** で、管理フロントエンド
   用のApplicationを作成する (Regular Web Application)。
   - Allowed Callback URLs: `<フロントエンドのURL>/auth/callback`
   - Allowed Logout URLs: `<フロントエンドのURL>`
   - Domain / Client ID / Client Secretを控えておく。

### 2. バックエンド (FastAPI) をResource Serverにする

- 依存追加: `pyjwt[crypto]`
- 環境変数: `AUTH0_DOMAIN` / `AUTH0_AUDIENCE` (手順1のAPI Identifier)
- JWT検証の依存性を実装する (このリポジトリでは `app/core/auth.py`):
  - `PyJWKClient`でAuth0のJWKSエンドポイント
    (`https://<AUTH0_DOMAIN>/.well-known/jwks.json`) から署名鍵を取得する。
  - 署名 (RS256) / `aud` / `iss` / 有効期限を検証する。
  - 検証に失敗したら401を返す (`WWW-Authenticate: Bearer`)。
- 保護したいルーターにこの依存性を適用する
  (`app/api/v1/items.py`の`dependencies=[Depends(verify_token)]`)。
- 401をOpenAPIスキーマの`responses=`に明記する (契約テストで検知できるように
  するため)。

### 3. フロントエンド (Next.js) にログインを組み込む

- 依存追加: `@auth0/nextjs-auth0` (v4)
- 環境変数: `AUTH0_DOMAIN` / `AUTH0_CLIENT_ID` / `AUTH0_CLIENT_SECRET` /
  `AUTH0_SECRET` (`openssl rand -hex 32`で生成) / `AUTH0_AUDIENCE` (バックエンド
  と同じ値)
- `Auth0Client`をインスタンス化し (`admin/lib/auth0.ts`)、
  `authorizationParameters.audience`にバックエンドのAPI Identifierを指定する。
  これにより、発行されるアクセストークンがそのAPI向けの (`aud`がAPIの
  Identifierと一致する) ものになる。
- Next.js 16では`proxy.ts`で認証ミドルウェアを配線する
  (`auth0.middleware(request)`)。v4 SDKは`/auth/login` `/auth/logout`
  `/auth/callback`等のルートを自動でマウントするため、自分でルートハンドラを
  書く必要はない。
- FastAPI呼び出し時は`auth0.createFetcher(...).fetchWithAuth()`を使うと、
  アクセストークンが自動的に`Authorization: Bearer`ヘッダーへ付与される
  (`admin/lib/api.ts`)。
- 未ログイン時は`/auth/login`へのリンクを、ログイン済みなら`/auth/logout`への
  リンクを表示する。

### 4. デプロイ・環境変数の設定

- バックエンド: `AUTH0_DOMAIN` / `AUTH0_AUDIENCE`をホスティング先の環境変数に
  設定する。
- フロントエンド: `AUTH0_DOMAIN` / `AUTH0_CLIENT_ID` / `AUTH0_CLIENT_SECRET` /
  `AUTH0_SECRET` / `AUTH0_AUDIENCE` / `API_BASE_URL` (バックエンドの公開URL) を
  設定する。
- Auth0側のApplicationに、実際のフロントエンドURLでのCallback URL/Logout URL
  を追加登録する。
- 環境変数を後から追加・変更した場合、多くのホスティングサービスでは
  **再デプロイしないと反映されない**点に注意する。

## Stage 2: Microsoft Entra IDのブローカー化 + RBAC

### 1. Entra ID側: アプリの登録

1. Azure Portal (`portal.azure.com`) → **Microsoft Entra ID → アプリの登録 →
   新規登録**。
2. 名前は任意 (例: `my-admin`)。サポートされているアカウントの種類は
   「シングル テナントのみ」で十分。
3. リダイレクトURI (プラットフォーム: Web) に
   `https://<AUTH0_DOMAIN>/login/callback` を設定する。
4. 登録後、「証明書とシークレット」で新しいクライアントシークレットを発行する
   (値は発行直後しか表示されないので、その場で控える)。
5. 「概要」から「アプリケーション(クライアント)ID」と
   「ディレクトリ(テナント)ID」を控える。

### 2. Auth0側: Enterprise Connectionの作成

1. **Authentication → Enterprise → Microsoft Azure AD (Entra ID)** で新規
   Connectionを作成する。
2. Client ID / Client Secret / Domain (またはTenant ID) に、手順1で取得した
   値を設定する。
3. 作成したConnectionの **Applications** タブで、管理フロントエンド用の
   Applicationを有効化する (自動生成されるM2M用のTest Applicationは有効化
   不要)。
4. Connectionの「Connection Name」を控えておく (フロントエンドからこの
   Connectionを直接指定してログインする際に使う)。

### 3. Auth0側: RBAC (ロールベース認可) の設定

1. **Applications → APIs** → Stage 1で作成したAPIを開き、**RBAC Settings**
   で「Enable RBAC」と「Add Permissions in the Access Token」を有効化する。
2. **Permissions** タブで、制限したい操作に対応するpermission文字列を追加する
   (例: `delete:items`。Descriptionは必須項目)。
3. **User Management → Roles** でロールを作成し (例: `admin`)、Permissions
   タブで上記permissionを割り当てる。
4. **User Management → Users** で該当ユーザーを開き、Rolesタブでロールを
   割り当てる。
   - 注意: **同じメールアドレスでも、ログインに使った接続 (Username-Password
     / Google / Entra IDなど) ごとにAuth0上では別ユーザーとして扱われる**。
     Entra ID経由でログインしたユーザーには、そのユーザー (Connectionが対象の
     Enterprise Connectionになっているエントリ) に別途ロールを割り当てる
     必要がある。
   - 注意: ロール割り当て前に発行済みのアクセストークンには新しいpermission
     は含まれない。一度ログアウトし再ログインすることで反映される。

### 4. バックエンド: permissionチェックの実装

- 検証済みJWTの`permissions`クレームを見て、指定したpermissionを持たない
  リクエストを403にする依存性ファクトリを実装する
  (`app/core/auth.py`の`require_permission(permission)`)。
- 制限したいエンドポイントにのみ適用する
  (`Depends(require_permission("delete:items"))`)。他のエンドポイントは
  Stage 1同様、認証さえされていれば従来通り許可する。
- 403を`responses=`に明記する。

### 5. フロントエンド: Entra IDログインの導線とエラー表示

- 環境変数 `AUTH0_ENTERPRISE_CONNECTION` に、手順2で控えたConnection Name
  を設定する。
- ログイン導線に、通常ログイン (`/auth/login`) とは別に、
  `/auth/login?connection=<Connection Name>` へのリンクを設ける。この
  環境変数が未設定の場合は、この導線自体を表示しない (Stage 1の通常ログイン
  のみになる)。
- API呼び出しが403 (権限不足) を返した場合、汎用的なエラー画面に落とさず、
  権限が無いことをユーザーに表示する (`admin/lib/api.ts`の`ForbiddenError`)。

## つまずきやすい点 (このリポジトリの構築時に実際に発生した事象)

- Auth0の「API」のIdentifierは作成後に変更できない。誤字に気づいたら作り直す
  しかない。
- Auth0のAPIの Access Policy (「Within user-delegated access」) が
  「Per-app authorization」になっていると、Applicationからそのpermissionを
  要求してもエラーになる。動作確認中は「All apps allowed」にしておくと
  迷わない。
- テナントに既存の無関係なRule/Actionが残っていると、ログインパイプライン
  全体がエラーになることがある。心当たりのないエラーが出た場合は
  Auth Pipeline > Rules と Actions > Library > Customを確認する。
- Next.jsのServer Actionsは、ページの認証チェックとは独立に外部から直接
  呼び出せるHTTPエンドポイントである。ページ側の認証チェックだけに頼らず、
  Server Action自身の中でもセッションを確認する。
- ルートページなどで未ログイン時に`redirect()`で強制的に飛ばしてしまうと、
  そのページ (やレイアウト) 自身が用意したログイン導線が表示される前に
  遷移してしまう。ログインの選択肢を提示したいページでは、リダイレクトでは
  なくページ自身が未ログイン用のUIを描画する必要がある。

---

繰り返しになるが、本ガイド中の具体的な値 (ドメイン名・API Identifier・
Connection Name・ロール名・permission文字列など) はすべて例である。実際の
名称は自由に決めてよく、決めた値と環境変数・各ダッシュボードの設定を
一致させることだけが必要である。
