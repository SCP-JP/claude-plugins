# 03 — モジュール全一覧（ListPages 以外）

一次情報: `www.wikidot.com/doc-modules:*`（全49ページ）
ListPages / CountPages は `02-listpages.md` を参照。

```
[[module ModuleName arg="値"]]
本文（モジュールによる）
[[/module]]
```
モジュール名は大文字小文字を区別しない（`[[module css]]` も動く）。

---

## 1. 一覧・分類系

| モジュール | 用途 |
|---|---|
| `ListPages` | ページの選択・整形・列挙（→ 02） |
| `CountPages` | 件数カウント（→ 02） |
| `ListUsers` | ユーザー情報の出力 |
| `ListDrafts` | 下書きのあるページ一覧 |
| `TagCloud` | タグクラウド |
| `PageCalendar` | 年月別のページ数カレンダー |
| `PageTree` | 親子関係のツリー |
| `Backlinks` | 現ページへリンクしているページ |
| `WantedPages` | 存在しないがリンクされているページ |
| `OrphanedPages` | どこからもリンクされていないページ |
| `Categories` | サイト内カテゴリ一覧（ListPages で代替可） |

### ListUsers
```
[[module ListUsers users="."]]
あなたは %%number%% 番、%%title%% (%%name%%) です
[[/module]]
```
- 現在の**実装は `users="."`（＝閲覧中のログインユーザー）のみ**が実質使える
- 変数: `%%number%%`（ユーザーID）, `%%title%%`（表示名）, `%%name%%`（unix名）
- **匿名ユーザーには何も出力されない**（＝HTML化すらされない）。この性質がサインイン/非サインイン分岐に使われる（→ 06）
- 本文に `[[code]]` / `[[html]]` は入れられない

### ListDrafts
`pageType="exists"` / `"notexists"`。無指定なら全部。

### TagCloud
`mode="3d"` / `maxFontSize` / `minFontSize` / `maxColor` / `minColor`（`R,G,B` 0-255）/ `limit`（既定50）/ `target`（既定 `system:page-tags`）/ `category` / `showHidden` / `urlAttrPrefix` / `skipCategoryFromUrl` / `width` / `height`
フォントサイズ・色は max と min の両方を同じ単位で指定しないと効かない。

### PageCalendar
`category` / `tags` / `startPage`(=`targetPage`) / `urlAttrPrefix`。`@URL` 対応。ListPages と組み合わせるときは `urlAttrPrefix` を両者で揃える。

### PageTree
`root`（既定は現ページ）/ `showRoot` / `depth`

### Backlinks
属性なし。`div.backlinks-module-box` でスタイル可能。
**応用**: `category:` 名前空間にページを作り、そこに Backlinks を置くと「ソフトカテゴリ」が作れる。

---

## 2. ユーザー・メンバー系

| モジュール | 主な引数 |
|---|---|
| `Watchers` | `noActions="true"` |
| `Members` | `group="members\|admins\|moderators"`, `showSince`, `order="userId\|joined\|name(+Desc)"` |
| `Join` | `button="…"`, `class="…"`（既定クラス `.join-box`）。既にメンバーだとボタンが出ないので確認はプレビューかサインアウトで |
| `SendInvitations` | — |
| `WhoInvited` | — |

---

## 3. その他

### CSS モジュール（最重要）
```
[[module CSS]]
#side-bar { visibility: hidden; width: 0 }
@import url(…);
[[/module]]
```
- `show="true"` … CSS を `[[code type="css"]]` としてページに表示する
- `disable="true"` … CSS を無効化する
- **1ページに何個でも置ける**。出力順に HTML の head に並ぶ
- クロスサイトインクルード（CSI）と組み合わせるのが本来の用途

### NewPage
`category` / `template`（`template:` カテゴリのページ。カンマ区切りで複数）/ `size` / `button` / `format`（PCRE 正規表現）/ `tags` / `parent` / `mode`(`edit`/`save-and-refresh`/`save-and-go`) / `goTo`
**`_` 始まりの隠しページは作れない**（`_template` は URL 直打ちで作る）。

### Redirect
`destination="page-name"` または URL。末尾スラッシュでパスマッピング。
編集するには `…/page/noredirect/true`。

### ThemePreviewer
`noUi="true"` で UI を隠し、`?theme_url=…` で指定したテーマを適用。

### MailForm
フォーム定義を入れ子リストで書き、送信内容をメールで受け取る。
```
[[module MailForm to="user-name" button="送信" title="件名" format="csv" successPage="thanks"]]
# field_name
 * title: 表示名
 * type: text | textarea | select | checkbox
 * size: 30
 * default: 初期値
 * hint: 補足
 * options:
  * key: 表示値
 * rules:
  * required: true
  * minLength: 2
  * maxLength: 500
  * match: /正規表現/
  * number: true
  * minValue: / maxValue:
[[/module]]
```
`to` にスペースを含むユーザー名を書くときはハイフンかアンダースコアに置換する。省略時はサイト管理者宛。
→ 矛盾するバリデーション（`maxLength:10` と `minLength:100`）を書くと**絶対に送信できない偽の入力欄**が作れる（SCP-JP の `component:fakeprot`）。

### PetitionAdmin / SiteGrid / FeaturedSite / Clone / ManageSite
- `SiteGrid` は本文にサイト名を改行区切りで列挙。`limit` でランダムに n 件表示
- `Clone` は `source` / `button`
- `ManageSite` はサイト管理

---

## 4. ニュース・フィード

### Feed
```
[[module Feed src="URL1;URL2" limit="20" offset="0"]]
++ %%linked_title%% (%%linked_channel_title%%)
%%date|%e %b %Y%%
%%description%%
[[/module]]
```
変数: `%%title%%` `%%linked_title%%` `%%channel_title%%` `%%linked_channel_title%%` `%%link%%` `%%description%%`(=`%%short%%`,`%%summary%%`) `%%content%%`(=`%%long%%`,`%%body%%`) `%%date%%` `%%date|format%%` `%%custom <パス>%%`

`%%custom%%` は任意のフィード要素にアクセスする。`%%custom digg:diggCount%%`、ネストは `/` 区切り、ルートからは `feed/channel/title`。`[[image]]` の中で使う場合はスペースをアンダースコアに置換する。

### FrontForum
フォーラムのスレッドをニュース記事として表示する。`category`（フォーラムカテゴリの数値ID、`;` 区切り）/ `feed` / `feedTitle` / `limit` / `offset` / `fixRelativeLinks`
変数: `%%title%%` `%%linked_title%%` `%%link%%` `%%author%%` `%%date%%` `%%date|format%%` `%%comments%%` `%%category%%` `%%description%%` `%%content%%`

---

## 5. フォーラム・コメント

| モジュール | 引数 |
|---|---|
| `Comments` | `title` / `hide="true"` / `hideForm="true"` / `order="reverse"` |
| `RecentPosts` | なし |
| `MiniRecentThreads` | `limit`（既定5） |
| `MiniActiveThreads` | `limit`（直近7日で活発なスレッド） |
| `MiniRecentPosts` | `limit` |

---

## 6. 評価

### Rate
```
[[module Rate]]
```
サイトマネージャで評価が有効なこと。5つ星モードでは本文に変数を書ける。
`%%rating%%` / `%%rating_votes%%` / `%%rating_percent%%` / `%%rating_decimal%%`

生成される DOM（改造の要）:
`div.page-rate-widget-box` > `.rate-points`(`> .number`) / `.rateup` / `.ratedown` / `.cancel`

### RatedPages
`category` / `order`(`date-created-asc|desc`, `rating-asc|desc`) / `minRating` / `maxRating` / `limit` / `comments`

---

## 7. 画像・ファイル

- `Gallery` … 構文側 `[[gallery]]`（→ 01）
- `FlickrGallery`
- `Files` … 現ページの添付一覧

---

## 8. 検索

| モジュール | 必須ページ |
|---|---|
| `Search` | `search:site` にも同じモジュールが必要。引数 `mini="true"`, `a="p\|f\|pf"` |
| `SearchAll` | `search:all` |
| `SearchUsers` | `search:users` |

検索クエリ構文: `+word`（必須） / `title:word` / `title:"複数語"` / `ele*` / `ele*ant` / `category:abc,def` / `since:yyyy-mm-dd` / `till:yyyy-mm-dd` / `user:author-name` / 全体検索では `site:name`。タグ検索は性能上の理由で無効化されている。

---

## 9. 変更履歴

`SiteChanges` … 新規ページ、本文/タイトル編集、リネーム、親変更、添付操作を列挙。フォーラム活動は含まない。

---

## 10. 非推奨

`AdSenseUnit` / `MembershipApply` / `MembershipByPassword` / `Pages` / `ChildPages` / `PagesByTag` / `NextPage` / `PreviousPage` / `SimpleToDo`
いずれも ListPages で置き換えるのが正しい。

---

## 11. カスタムレイアウト用モジュール（Pro のみ、`<body>` 内テンプレート）

`[[module NaviBar]]` `[[module FooterBar]]` `[[module LoginStatus]]` `[[module PageOptionsBottom]]` `[[action_area]]`
`[[site_name]]` `[[site_subtitle]]` `[[content]]` `[[search_box]]` `[[site_locked]]` `[[page_title]]` `[[breadcrumbs]]` `[[tags]]` `[[topbar]]` `[[sidebar]]` `[[ssl_warning]]` `[[page_not_exists]]` `[[license_text]]` `[[footer]]`

条件分岐:
```
[[if name]] … [[/if]]
[[if !name]] … [[/if]]
[[if name]] … [[else]] … [[/if]]
```
使える条件: `site_subtitle` `site_locked` `page_title` `breadcrumbs` `tags` `topbar` `sidebar` `ssl_warning` `page_exists` `license_text` `custom_footer`
