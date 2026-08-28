# 04 — サイト構造・テンプレート・DOM・データフォーム

一次情報: `www.wikidot.com/doc:site-structure`, `doc:templates`, `doc:layout-reference`, `doc-data-forms:*`, `doc:searching`, `doc:thumbnails`, `doc:api`

---

## 1. サイトとページ

- 1サイト = `http://<site-unix-name>.wikidot.com`。unix名は `[0-9a-z-]` のみ。
- ページは**フラット構造**。ディレクトリは存在しない。ページの unix 名は `[0-9a-z-:]`。
- `category:name` の `:` より前が**カテゴリ（名前空間）**。カテゴリはページ作成で自動生成され、そのカテゴリのページが0になると自動削除される。
- カテゴリ単位で **テーマ・権限・ライセンス・テンプレート** を設定できる。
- **タグ**は機能に影響しない純粋なラベル（カテゴリと対照的）。1タグ64文字まで、個数無制限。`_` 始まりは隠しタグ。
- **親ページ**（parent）はパンくずリストを生成し、`PageTree` / ListPages の `parent` セレクタで使う。
- ファイルは `http://site.wikidot.com/local--files/<page>/<file>`、CDN は `http://site.wdfiles.com/local--files/…`。**HTTPS の wdfiles リンクは HTTPS 非対応のサンドボックスでも動く**。

## 2. `_template`

カテゴリ内の全ページに共通レイアウトを適用する仕組み。

- ページ名は `<category>:_template`。既定カテゴリなら `_template`。
- 最低限 `%%content%%` を書く必要がある。空だと機能しない。
- `_` 始まりのページなので **NewPage モジュールでは作れない**。URL に直接 `category:_template` を打って作成する。
- テンプレートを編集すると、そのカテゴリの全ページが再コンパイルされる。
- `_` 始まりのページ自身にはテンプレートが適用されない。

```
[[div style="float:right; width: 200px;"]]
%%content{1}%%
[[/div]]
%%content{2}%%
====
サイドバーになる部分
====
本文になる部分
```

### 新規ページの初期本文
`_template` 内で `====` の後ろに書いた内容は、**そのカテゴリで新規ページを作るときのエディタ初期値**になる。視認性のため `==========` のように長くするのが慣習。初期本文を定義すると `templates:` カテゴリからのテンプレート選択は出なくなる。

### `_template` で使える変数
ListPages と同じ変数群（`01`/`02` 参照）に加えて、404 テンプレートでは `%%404_page_name%%`。

### 404 テンプレート
- `<site>/_404` … サイト全体の「ページが存在しません」表示を差し替える
- `<site>/category:_404` … カテゴリ単位
```
+ ページが見つかりません: //%%404_page_name%%//
[[button edit text="作成する"]]
```

## 3. ページ DOM 構造（CSS を書くための地図）

```
div#container
 ├ div#header
 │   ├ h1 > a > span            サイト名
 │   ├ h2 > span                サブタイトル
 │   ├ div#top-bar              トップナビ
 │   ├ div#login-status
 │   └ div#header-extra-div-1..3 > span
 ├ div#content-wrap
 │   ├ div#side-bar
 │   └ div#main-content
 │        ├ div#action-area-top
 │        ├ div#page-title
 │        ├ div#breadcrumbs
 │        ├ div#page-content          ← 本文
 │        ├ div#page-info
 │        ├ div#page-options-bottom(.page-options-bottom)
 │        ├ div#page-options-bottom-2
 │        └ div#action-area
 ├ div#footer > div.options
 └ div#license-area
div#extra-div-1..6 > span
```
外側には `#container-wrap`, `#container-wrap-wrap`, `#skrollr-body` も存在する（SCP-JP のエフェクト系 CSS が疑似要素を生やす先）。

主なコンポーネントのクラス:
- 評価: `div.page-rate-widget-box` > `.rate-points > .number` / `.rateup` / `.ratedown` / `.cancel`
- 折り畳み: `div.collapsible-block` > `.collapsible-block-folded` / `.collapsible-block-unfolded` > `.collapsible-block-content`、リンクは `a.collapsible-block-link`
- タブ: `div.yui-navset` > `ul.yui-nav > li(.selected)` / `div.yui-content > div#wiki-tab-0-N`（**id はコンパイルごとにランダム**）
- 脚注: `div.footnotes-footer > div.title` / `div.footnote-footer#footnote-N`、ホバーは `.hovertip > .content`
- テーブル: `table.wiki-content-table`
- バックリンク: `div.backlinks-module-box`
- 画像ブロック（SCP系）: `.scp-image-block` / `.scp-image-caption`

## 4. カスタムレイアウト（Pro）

`<body>` 内の HTML 構造そのものを差し替えられる。`<body>` タグと `id=""` は使用不可。使えるモジュール/プレースホルダと `[[if]]` は `03-modules.md` の末尾参照。

## 5. データフォーム（Data Forms）

カテゴリに構造化フィールドを定義し、ページを「レコード」として扱う機能。

- 定義は `<category>:_template` の中に `[[form]] … [[/form]]` を書く（YAML風の入れ子）
- フィールド型: `text` / `textarea`(wiki) / `select` / `checkbox` / `date` / `file` / `hidden` / `password` / `static` / `url` / `pagepath` / `wiki`
- 表示は `%%form_data{名}%%`、選択肢の内部値は `%%form_raw{名}%%`、ラベルは `%%form_label{名}%%`、ヒントは `%%form_hint{名}%%`
- ListPages では `_フィールド名="値"` で絞り込み、`order="_フィールド名::integer desc"` で数値ソート
- **wiki 型フィールドの表示には `%%form_raw{…}%%` を使う**（`%%form_data%%` ではない）

SCP系ではほぼ使われないが、サンドボックスの下書き管理システム等で利用例がある。

## 6. 検索構文

`+word` 必須 / `title:word` / `title:"複数語"` / `ele*` / `ele*ant`
フィルタ: `category:abc,def` / `since:yyyy-mm-dd` / `till:yyyy-mm-dd` / `user:author-name`
全体検索(`www.wikidot.com/search:all`)では `site:name` が追加で使える。
タグ検索は性能上の理由で無効化されている。

## 7. サムネイル

```
http://thumbnail.wdfiles.com/thumbnail/site/<domain>/<160|80|40|20>.jpg
http://thumbnail.wdfiles.com/thumbnail/theme/<theme-unix-name>/<500|240|160|80>.jpg
```

## 8. Wikidot API / 外部からの操作

- 公式 XML-RPC API（`doc:api`）は Pro 限定・機能も限定的。
- 実務では **AJAX Module Connector（`/ajax-module-connector.php`）** を叩くライブラリが使われる。Python なら `ukwhatn/wikidot.py`（PyPI: `wikidot`）。
- `wikidot.py` でのソース一括取得例は `scripts/fetch_wikidot_sources.py` を参照。

### 調査に使える URL 群
| URL | 内容 |
|---|---|
| `…/printer--friendly//<page>` | サイドバー等を剥いだ本文 |
| `…/<page>/norender/true` | レンダリングせず開く（壊れたページの救出） |
| `…/<page>/noredirect/true` | Redirect モジュールを無効化 |
| `…/<page>#_editpage` | 編集画面を直接開く |
| `…/<page>/code` , `…/<page>/code/N` | コードブロックの生データ |
| `…/<page>/code_` , `…/<page>/code_/N` | `_template` 適用後のソースから抽出 |
| `http://<site>.wdfiles.com/local--code/<urlencodedページ名>/N` | 同上（CDN 経由） |
| `…/system:recent-changes` `system:list-all-pages` `system:page-tags` | システムページ |
| ページ下部 Options → Page Source | そのページの完全なソース |
