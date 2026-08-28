# 02 — ListPages / CountPages 完全リファレンス

一次情報: `www.wikidot.com/doc-modules:listpages-module`, `doc-include:page-selection`, `doc-modules:countpages-module`, `doc:templates`
実践事例: `shitake-crude-production.wikidot.com/specification:listpagesmodule-study`

```
[[module ListPages 引数...]]
本文テンプレート
[[/module]]
```
既定では「現在のカテゴリの可視ページを新しい順に全件」。

---

## 1. ページ選択セレクタ

複数指定は AND で絞り込まれる。同じセレクタ群は CountPages でも使える。

| 引数 | 意味 |
|---|---|
| `pagetype` | ページ種別 |
| `category` | カテゴリ |
| `tags` | タグ |
| `parent` | 親ページ |
| `link_to` | 発リンク先 |
| `created_at` | 作成日 |
| `updated_at` | 更新日 |
| `created_by` | 作成者 |
| `rating` | 評価値 |
| `votes` | 投票数 |
| `offset` | 先頭n件をスキップ |
| `range` | 現ページとの相対範囲 |
| `name` | ページ名（カテゴリ抜き） |
| `fullname` | フルネーム |
| `_<dataform項目名>` | データフォームの値 |

### pagetype
`normal`（`_`で始まらない、既定） / `hidden`（`_`始まり） / `*`（両方）

### category
- `.` 現カテゴリ（既定）
- `*` 全カテゴリ
- スペース/カンマ区切りの複数指定は OR
- `-category` 除外（AND NOT）
- `%%category%%` `_template` 内で「自分と同じカテゴリ」

### tags
- `-` タグを1つも持たないページ
- `=` 自分と同じ可視タグをどれか持つページ
- `==` 可視タグが完全一致するページ
- スペース/カンマ区切りは OR
- `+tag` AND / `-tag` AND NOT
- URL 経由で `+` を渡すときは `%2b` にエンコードする

### parent
- `-` 親なし
- `=` 自分の兄弟（同じ親）
- `-=` 自分と違う親
- `.` 自分の子
- それ以外は単一のフルページ名

### link_to
- 既存ページのフルネーム = そのページへリンクしているページ
- `.` = 現ページへリンクしているページ

### created_at / updated_at
- `=` 現ページと同日
- `yyyy` / `yyyy.mm`
- `>` `<` `=` `<=` `>=` `<>` を前置可（既定は `=`）
- **日付はサイトのローカル時刻ではなく常に UTC**
- `last n unit` / `older than n unit`（unit は `hours` / `day` / `week` / `month`、n 既定 1）

### created_by
`=` 現ページの著者 / `-=` 現ページの著者以外 / ユーザー名

### rating / votes
数値、`=`（現ページと同じ）、比較演算子前置。
**注意**: サイトマネージャで評価タイプ（`+`, `+/-`, stars）が異なるカテゴリを跨いで rating で選択・整列すると正常動作しない。

### offset / range
- `offset="n"` 先頭 n 件を出さない
- `range`: `.` 現ページ / `before` 現ページより前 / `after` 現ページより後 / `others` 現ページ以外

### name / fullname
- `name="scp-173"` カテゴリ抜きの名前で指定
- `name="="` 現ページと同名
- `name="s%"` または `name="s*"` 前方一致
- `fullname="category:page"` 完全一致で1ページ

### データフォーム
`_gender="m"` のように `_` + フィールド名。

---

## 2. 並び順

```
order="rating desc"
order="created_at"
order="random"                      60秒キャッシュ
order="_albums::integer desc"       データフォーム値を数値としてソート
```
使えるプロパティ: `name, fullname, title, created_by, created_at, updated_at, size, rating, votes, revisions, comments, random, _<dataform>`

- ` desc` で降順。` desc desc` で昇順（安全に `desc` を後置できる）
- `プロパティ asc` は**不正**。不正な指定は既定（`created_at desc`）に落ちる

---

## 3. ページネーション

| 引数 | 意味 |
|---|---|
| `limit` | 総件数の上限 |
| `perPage` | 1ページあたりの表示件数（既定20、最大250） |
| `reverse="yes"` | そのページ内で逆順表示 |

---

## 4. 本文テンプレート

| 引数 | 意味 |
|---|---|
| `separate` | `yes`(既定) 各ページを別コンテナ(div)に入れる / `no` 全部を1コンテナに |
| `wrapper` | `yes`(既定) 全体を div で包む / `no` 包まない |
| `prependLine` | 先頭に出力するテキスト（`separate="no"` のときのみ） |
| `appendLine` | 末尾に出力するテキスト（同上） |

**`separate` はコンパイル単位を変える**：
- `yes` … ページごとに個別にコンパイル。`[[iftags]]` は**各ページのタグ**を見る。`[[image :first]]` が機能する。
- `no` … 全件を結合してから1回だけコンパイル。`[[iftags]]` は**モジュールを置いた親ページのタグ**を見る。`[[image :first]]` は機能しない。

### head / body / foot セクション
`prependLine` / `appendLine` の上位互換。テーブルやリストの組み立てに使う。
```
[[module ListPages category="carousel" wrapper="no" separate="no"]]
  [[head]] [[ul class="my-list"]] [[/head]]
  [[body]] [[li]]%%title_linked%% by %%created_by%%[[/li]] [[/body]]
  [[foot]] [[/ul]] [[/foot]]
[[/module]]
```

---

## 5. 変数一覧

### ページのライフサイクル
`%%created_at%%` `%%created_by%%` `%%created_by_unix%%` `%%created_by_id%%` `%%created_by_linked%%`
`%%updated_at%%` `%%updated_by%%` `%%updated_by_unix%%` `%%updated_by_id%%` `%%updated_by_linked%%`
`%%commented_at%%` `%%commented_by%%` `%%commented_by_unix%%` `%%commented_by_id%%` `%%commented_by_linked%%`

### ページ構造
`%%name%%` `%%category%%` `%%fullname%%` `%%title%%` `%%title_linked%%`
`%%parent_name%%` `%%parent_category%%` `%%parent_fullname%%` `%%parent_title%%` `%%parent_title_linked%%`
`%%link%%`（カスタムドメインでは機能しない）
`%%content%%` `%%content{n}%%` `%%preview%%` `%%preview(n)%%` `%%summary%%` `%%first_paragraph%%`
`%%tags%%` `%%tags_linked%%` `%%tags_linked|接頭辞%%` `%%_tags%%` `%%_tags_linked%%` `%%_tags_linked|接頭辞%%`
`%%form_data{名}%%` `%%form_raw{名}%%` `%%form_label{名}%%` `%%form_hint{名}%%`

### 集計
`%%children%%` `%%comments%%` `%%size%%` `%%rating%%` `%%rating_votes%%` `%%rating_percent%%` `%%revisions%%`
`%%index%%`（出力内の連番＋offset） `%%total%%`（limit無視の総数） `%%limit%%`（渡された limit、無ければ空） `%%total_or_limit%%`

### 文脈
`%%site_title%%` `%%site_name%%` `%%site_domain%%`

### 日付フォーマット
`_at` 系はすべて `|フォーマット` を後置できる。PHP strftime のトークン＋`%O`（相対時間）。
```
%%created_at|%Y年%m月%d日 %H:%M|agohover%%
```

### tags_linked のリンク先制御
| 記法 | リンク先 |
|---|---|
| `%%tags_linked%%` | `/system:page-tags/tag/shiny` |
| `%%tags_linked\|interesting-list/category/%%` | `/interesting-list/category/shiny` |
| `%%tags_linked\|player:%%` | `/player:shiny` |
| `%%tags_linked\|%%` | `/shiny` |
| `%%tags_linked\|http://other.wikidot.com/see-also/tag/%%` | 外部サイトへ |

---

## 6. `====` によるコンテンツ分割と `%%content{n}%%`

ページ本文中に**単独行で `====`（イコール4つ以上）**を置くとコンテンツがセクションに分かれ、`%%content{1}%%`, `%%content{2}%%`… で個別に取り出せる。
- `%%content{1}%%` は最初のセクション
- `%%summary%%` / `%%short%%` はセクションがあれば最初のセクション、無ければ最初の段落
- `_template` でも同じ仕組みが使え、多段組レイアウトが作れる
- `_template` 側では `====` の後ろに「新規ページ作成時の初期本文」を書ける
- エスケープは `@@====@@` または末尾スペース

---

## 7. RSS

| 引数 | 意味 |
|---|---|
| `rss` | フィードタイトル（指定するとフィード生成） |
| `rssDescription` | 説明 |
| `rssHome` | フィードのホームページ |
| `rssLimit` | フィードの件数上限 |
| `rssOnly` | `true` でリンクのみ表示 |

**RSS は `created_at` セレクタを無視する。**

---

## 8. URL による引数渡し（ギミックの心臓部）

引数の値を `"@URL|デフォルト値"` または `"@URL"` にすると、URL のパス末尾から値を受け取る。

```
[[module ListPages category="@URL|design"]]
%%name%% in %%category%%
[[/module]]
```
→ `http://site.wikidot.com/page/category/tale/order/rating desc/limit/3`

- `@URL` を含まない引数は URL から設定できない
- デフォルト値は省略可。省略時に値が来なければ「その引数を指定しなかった」扱い
- タグの `+` は `%2b` にエンコード

### urlAttrPrefix
同一ページに複数の ListPages を置くと URL 引数が衝突する（片方の「次へ」が両方に効く等）。
```
[[module ListPages … urlAttrPrefix="page2"]]
```
→ URL 側は `…/page2_limit/1` になる。TagCloud / PageCalendar にも同名引数がある。

---

## 9. 制約と落とし穴

- **本文テンプレートに `[[code]]` / `[[html]]` を入れるとモジュールごと動作しない**（公式明記）。抜け道は `06-hacks-and-bugs.md` の `%%content{0}%%` 技。
- 他のほとんどのモジュールは ListPages の中に入れられない。
- ListPages はページを著しく重くする。1ページに複数置くのは非推奨（DrMagnus）。
- 評価タイプが異なるカテゴリを跨いだ rating の選択・整列は壊れる。
- 引数無し・`[[/module]]` 無しの「デフォルトフォーマット」は deprecated。
- `%%content{n}%%` は歴史的に「リストされたページではなく現在のページの内容を返す」不具合が報告されていた（現在は概ね修正済み）。

---

## 10. 非推奨引数・変数の対応表

| 旧 | 新 |
|---|---|
| `skipCurrent="yes"` | `range="others"` |
| `categories=` | `category=` |
| `tag=` | `tags=` |
| `tagTarget="pagename"` | `%%tags_linked\|/pagename/tag/%%` |
| `date=` | `created_at=` |
| `order="dateCreatedAsc/Desc"` | `order="created_at [desc]"` |
| `order="dateEditedAsc/Desc"` | `order="updated_at [desc]"` |
| `order="titleAsc/Desc"` | `order="title [desc]"` |
| `order="ratingAsc/Desc"` | `order="rating [desc]"` |
| `order="pageLengthAsc/Desc"` | `order="size [desc]"` |
| `rssTitle=` | `rss=` |
| `%%linked_title%%` | `%%title_linked%%` |
| `%%page_unix_name%%` / `%%full_page_name%%` | `%%fullname%%` |
| `%%page_name%%` | `%%name%%` |
| `%%author%%` / `%%author_edited%%` / `%%user_edited%%` | `%%created_by%%` / `%%updated_by%%` |
| `%%date%%` / `%%date_edited%%` | `%%created_at%%` / `%%updated_at%%` |
| `%%description%%` / `%%short%%` | `%%summary%%` |
| `%%text%%` / `%%long%%` / `%%body%%` | `%%content%%` |

---

## 11. CountPages

```
[[module CountPages category="wiki,blog" tags="_closed"]]
%%total%% 件
[[/module]]
```
- セレクタは ListPages と同一
- 使える変数は `%%total%%`（別名 `%%count%%`）のみ
- 本文に Wiki 構文（リンク等）は書ける
- ListPages の中には入れられない
