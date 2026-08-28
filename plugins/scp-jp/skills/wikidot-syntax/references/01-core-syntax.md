# 01 — Wikidot コア構文 完全リファレンス

一次情報: `www.wikidot.com/doc-wiki-syntax:*`（全38ページ）、`doc:quick-reference`、`doc:expressions`

## 目次
1. パーサモデル
2. 段落・改行・空白
3. インライン装飾
4. 文字サイズ・色
5. 見出しと目次
6. リスト
7. 定義リスト
8. 引用
9. 水平線・フロート解除
10. リンク
11. アンカー / Magic URI / Hash Magic URI
12. 画像・ギャラリー・添付ファイル
13. テーブル
14. 折り畳み・タブ・折り畳みリスト
15. 脚注・参考文献
16. 数式
17. 日付
18. include
19. iftags
20. code / html / embed / iframe
21. div / span / a / ul / li と `_` 付き変種
22. ボタン・ソーシャル・ユーザー
23. エスケープ・コメント
24. タイポグラフィ
25. 式構文（[[#if]] / [[#ifexpr]] / [[#expr]]）
26. 行頭必須タグ一覧

---

## 1. パーサモデル

- ページは **source（Wiki構文）** と **compiled（XHTML）** の2形態を持つ。閲覧時にコンパイル済みが返る。
- パーサは**行指向**。多くのブロックタグは「行頭にあり、同一行に他の文字（スペースすら）がない」ことを要求する。
- 変換順序が存在し、`[[include]]` は **`[[code]]` の中でもパースされる**（後述）。この「順序」がバグ利用技の温床（→ `06-hacks-and-bugs.md`）。
- ユーザー定義 `id` は出力HTMLで自動的に **`u-` プレフィックス**が付く（セキュリティ上の措置）。自分で `u-` を書いた場合は二重付与されない。
- `div` / `span` / `a` / `ul` / `ol` / `li` などで許可される属性は **`id`, `class`, `style`, `data-*` のみ**。

## 2. 段落・改行・空白

| 書き方 | 結果 |
|---|---|
| 空行2つ（＝間に空行1つ） | 段落分け `<p>` |
| 単なる改行 | `<br>` 相当の改行 |
| 行末に ` _`（半角スペース＋アンダースコア） | 段落を分けずに改行。アンダースコアの後ろに文字を置かないこと |
| 行末に `\`（引用ブロック内） | 次行と連結して1行にする |
| `~~~~`（チルダ4つ以上） | `<div style="clear:both">` 相当。フロート解除 |
| `@@ @@` / `@@@@` | 何もパースされない空要素。段落の隙間作りに使う定番 |

`* _` を連ねると空行を任意個数入れられる（通常の空行連打は1行に潰される）。

## 3. インライン装飾

```
//斜体//              **太字**            //**斜体かつ太字**//
__下線__              --打ち消し線--       {{等幅 teletype}}
通常^^上付き^^        通常,,下付き,,
##blue|事前定義色##   ##44FF88|16進カスタム色##
[[span style="color:red"]]任意span[[/span]]
[[span_ class="x"]]前後の空白を潰すspan[[/span]]
```

`{{...}}` は HTML の `<tt>` になる。**SCP-JP の jstyles を導入すると `<tt>` の意味が変わり、等幅表示は使えなくなる**（→ `05-scp-jp.md`）。

## 4. 文字サイズ

相対（現在サイズ基準）: `smaller` / `larger` / `n%` / `n em`
絶対: `xx-small` / `x-small` / `small` / `large` / `x-large` / `xx-large` / `n px`

```
[[size smaller]]小さく[[/size]]
[[size 150%]]1.5倍[[/size]]
[[size 1.5em]]1.5倍[[/size]]
[[size 18.75px]]18.75px[[/size]]
```
数値は小数点を含む1〜5桁。ネスト可。

## 5. 見出しと目次

```
+ 見出し1
++ 見出し2
+++ 見出し3
++++ 見出し4
+++++ 見出し5
++++++ 見出し6
+* 目次に載せない見出し1
++* 目次に載せない見出し2
```

```
[[toc]]                    通常の目次
[[f>toc]] / [[f<toc]]      右／左フロート目次
[[toc title="目次"]]       タイトル変更（title="" で非表示）
```
`[[toc]]` は `#toc` というブックマークを作る。個々の見出しは `#toc0`, `#toc1`… で参照できる。

## 6. リスト

```
* 箇条書き1
* 箇条書き2
 * ネスト（行頭スペースを1つ増やす）

# 番号付き1
# 番号付き2
 # ネスト

* 複数行にしたい項目 _
 2行目
```
箇条書きと番号付きは混在可能。

**上級リスト**（Bootstrap系テーマ向け）:
```
[[ul]]
 [[li class="item1" data-toggle="data1"]]項目1[[/li]]
 [[li style="color: red;"]]項目2
  [[ol]]
    [[li]]項目2.1[[/li]]
  [[/ol]]
 [[/li]]
[[/ul]]
```
`[[ul_]]` / `[[ol_]]` は前後の空白を除去する変種。

## 7. 定義リスト

```
: 用語1 : 説明
: 用語2 : 説明 _
2行目
```

## 8. 引用

```
> 引用文（">" の後に半角スペース必須）
>
>> 2段目の引用
> バックスラッシュで \
次行と連結できる
```

SCP系では **`[[div class="blockquote"]] ... [[/div]]`** も同じ見た目になる。行頭 `>` を付けずに済み、`>` と相性の悪い構文（テーブル等）を中に置ける。

## 9. 水平線・フロート解除

```
----      （ダッシュ4つ以上）水平線
~~~~      （チルダ4つ以上）float解除
```

## 10. リンク

### 内部リンク
```
[[[page-name]]]                       ページ名そのまま
[[[link "TO" a; pagE]]]               自動 unixify（表示は元の文字列）
[[[category: sample page]]]           カテゴリ付き
[[[some page| 表示テキスト]]]
[[[some page|]]]                      ページタイトルを表示テキストにする
[[[doc#toc1|セクション1]]]
[[[/|ホーム]]]
```

### 外部リンク / URL
```
http://example.com                    自動リンク
[http://example.com テキスト]
[[[http://example.com | テキスト]]]
*http://example.com                   別ウィンドウ
[*http://example.com テキスト]
[[a href="http://example.com" class="x" style="..." target="_blank"]]テキスト[[/a]]
[[a_ href="..."]]…[[/a]]              空白潰し変種
[# 空リンク]                          href="javascript:;" のダミー。メニュー構築用
[/category:page/opt1/opt2 テキスト]    自サイトへのパラメータ付き相対リンク
```
`[[a]]` は角括弧など通常リンクを壊す文字を含められ、リンクテキスト内でWiki構文が使える。

### メール
```
support@example.com
[support@example.com メールする]
```
自動でスクランブルされ、クライアント側で復号される（完全なスパム対策ではない）。

### InterWiki
```
[wikipedia:Albert_Einstein]
[wikipedia:Albert_Einstein アルベルト]
[wikipedia:it:Albert_Einstein アルベルト]
[google:free+wiki]
[dictionary:wiki]
```

## 11. アンカー / Magic URI / Hash Magic URI

```
[[# anchor-name]]           アンカー定義
[#anchor-name テキスト]      アンカー参照
```
※ `[[div id="x"]]` の id は出力で `u-x` になるので、参照は `[#u-x ...]`。

### Magic URI（URLでページ状態を操作）
| URL | 効果 |
|---|---|
| `…/page#_editpage` | 編集モードで開く |
| `…/page/title/whatever` | 未作成ページの初期タイトルを設定 |
| `…/page/parentPage/parent-name` | 未作成ページの親を設定 |
| `…/page/noredirect/true` | Redirectモジュールを無効化して開く |
| `…/page/tags/tag1,tag2` | タグをURLから設定 |
| `…/page/norender/true` | レンダリングせずに開く（**壊れたページの救出に必須**） |

### Hash Magic URI
`#_wantedpages` `#_orphanedpages` `#_draftpages` `#_editpage` `#_edittags` `#_history` `#_files` `#_sitetools`

## 12. 画像

```
[[image 画像ソース attr="値" ...]]
```

| 属性 | 値 |
|---|---|
| `link` | ページ名 / URL / `#anchor` / `#`（クリック無効）。先頭 `*` で別窓 |
| `alt` | 代替テキスト |
| `title` | ツールチップ |
| `width` / `height` | `"200px"` |
| `style` | CSS |
| `class` | CSSクラス |
| `size` | `square`(75x75) / `thumbnail`(長辺100) / `small`(240) / `medium`(500) / `medium640`(Flickrのみ) / `large`(1024, Flickr) / `original`(Flickr) |

画像ソースの種類:
| 記法 | 意味 |
|---|---|
| `http://…/x.jpg` | URL |
| `filename.jpg` | 現ページの添付 |
| `:first` | 現ページの最初の添付画像 |
| `/another-page/filename.jpg` | 別ページの添付 |
| `flickr:83001279` | Flickr |
| `flickr:149666562_debab08866` | Flickr（secret付き＝非公開画像） |

配置: `[[=image …]]` 中央 / `[[<image …]]` 左 / `[[>image …]]` 右 / `[[f<image …]]` 左フロート / `[[f>image …]]` 右フロート

`size` は PDF や PostScript にも効く（ImageMagick 由来）。

### ギャラリー
```
[[gallery size="thumbnail" order="name" viewer="no"]]
: image1.jpg link="page" alt="…"
: image2.jpg
[[/gallery]]
```
引数なしなら現ページの添付画像を全部並べる。既定で LightBox ビューアが付く。

### 添付ファイルへのリンク
```
[[file filename | 表示テキスト]]
[[file /another-page/filename | 表示テキスト]]
```
先頭スラッシュは「start ページの添付」を意味するので誤用注意。

## 13. テーブル

### 簡易テーブル
```
||~ 見出し1 ||~ 見出し2 ||~ 見出し3 ||
|| セル1 || セル2 || セル3 ||
|||| 2列結合セル || セル ||
|||||| 3列結合セル ||
|| || 空セルに挟まれたセル || ||
||< 左寄せ ||= 中央 ||> 右寄せ ||
|| セル内改行は _
アンダースコアで ||
```
`||` を余分に前置した数だけ colspan。`|| ||`（間にスペース）で空セル。
生成される table のクラスは `wiki-content-table`。

### カスタムテーブル
```
[[table class="wiki-content-table" style="border-collapse:collapse;"]]
[[row]]
[[hcell colspan="2" style="…"]]見出しセル[[/hcell]]
[[/row]]
[[row]]
[[cell rowspan="2"]]セル[[/cell]]
[[cell]]セル[[/cell]]
[[/row]]
[[/table]]
```
`[[table]]`→`<table>`, `[[row]]`→`<tr>`, `[[hcell]]`→`<th>`, `[[cell]]`→`<td>`。
`class` / `style` / `colspan` / `rowspan` が使える。ネスト可。
簡易テーブルで「長文セルに押し潰される問題」は `[[cell style="width:9em;"]]` で回避する。
有用な style: `border-collapse: separate` / `border-spacing: 4px` / `empty-cells: hide`。

## 14. 折り畳み・タブ

```
[[collapsible show="+ 開く" hide="- 閉じる" hideLocation="both" folded="no"]]
本文
[[/collapsible]]
```
- 既定の文言は `+ show block` / `- hide block`
- `hideLocation`: `top`(既定) / `bottom` / `both`
- `folded="no"` で初期展開
- タグは必ず単独行に置く
- **ネスト不可**（→ Colmod で代替、`06`参照）

```
[[tabview]]
[[tab タイトル1]]内容[[/tab]]
[[tab タイトル2]]内容[[/tab]]
[[/tabview]]
```
**公式に明記された制約**: TabView は目次・アンカーリンク・ブラウザの戻るを壊す。タブ内の見出しに TOC から飛べない。タブ内リンクから戻ると必ず最初のタブになる。素直なネストは不可。

### 折り畳みリスト
```
[[div class="foldable-list-container"]]
* 第1階層
 * 第2階層
  * 第3階層
[[/div]]
```

## 15. 脚注・参考文献

```
本文[[footnote]]脚注内容[[/footnote]]。
[[footnoteblock]]                       脚注一覧の表示位置を指定
[[footnoteblock title="注記"]]           タイトル変更（title="" で消す）
```
生成HTML: `div.footnotes-footer > div.title` ＋ `div.footnote-footer#footnote-N`（Nは脚注番号）。ホバー時のウィンドウは `.hovertip` / `.hovertip .content`。

```
[[bibliography]]
: label : 完全な参考文献
[[/bibliography]]
本文 [((bibcite label))]
[[bibliography title="参考文献"]]
```

## 16. 数式（MathJax）

```
[[math ラベル]]
\rho = -\sigma(r)
[[/math]]

[[$ E = mc^2 $]]            文中数式
[[eref ラベル]]              式番号の参照
[[math type="align"]] … [[/math]]
```
既定環境は `equation`。他に `align, alignat, aligned, alignedat, array, Bmatrix, bmatrix, cases, eqnarray, gather, gathered, matrix, multline, pmatrix, smallmatrix, split, subarray, Vmatrix, vmatrix`。

## 17. 日付

```
[[date 1216153821]]
[[date 1216153821 format="%d. %m. %Y|agohover"]]
[[date 681746400 format="James is %O young"]]
```
- timestamp は UNIX 秒
- `format` は PHP strftime のトークン＋独自の `%O`（「〜前」の相対表現）
- `|agohover` でマウスオーバー時に相対時間を表示
- `%O` は未来日付にも使える

## 18. include

```
[[include pagename]]
[[include :sitename:pagename]]          クロスサイトインクルード(CSI)
[[include pagename
|var1=値1
|title=値2
]]
```
インクルードされる側では `{$var1}` `{$title}` のように書く。

**重要な仕様**
- `[[include]]` は **`[[code]]` ブロックの中でもパースされる**。回避するには行頭に半角スペースを1つ置く。
- インクルード元の添付ファイルを参照するときは `[[image included-page/filename.jpg]]` のようにページ名を付ける。
- sitename は Wikidot サブドメイン（`:www`）でもカスタムドメインでも良い。
- **同名引数を2回書くと後勝ちで、かつ解決は下から行われる**。これを利用してデフォルト値を実装できる（→「深層インクルード」、`06`参照）。

## 19. iftags

```
[[iftags +tag1 -tag2 tag3]] … [[/iftags]]
```
- `+tag` / 修飾子なし = そのタグが必要
- `-tag` = そのタグが無いこと
- `_` 始まりのタグは「隠しタグ」でタグクラウドに出ないが iftags/ListPages の条件には使える
- タグは64文字まで、スペース区切り、個数無制限
- `[[iftag]]`（単数形）も見かける

## 20. code / html / embed / iframe

### code
```
[[code]]…[[/code]]
[[code type="php"]]…[[/code]]
```
- 対応 type: `php, html, cpp, css, diff, dtd, java, javascript, perl, python, ruby, xml`
- 中身は `[[include]]` を除きすべてリテラル
- **各コードブロックには固有URLがある**:
  - `http://site.wikidot.com/category:page/code` （1つ目）
  - `http://site.wikidot.com/category:page/code/2` （2つ目）
  - `…/code_` / `…/code_/2` は `_template` 適用後のソースから抽出
  - CDN 経由の別形式: `http://site.wdfiles.com/local--code/<URLエンコードしたページ名>/1`
- これにより Wikidot を **CSS/JS の配信元**として使える（SCP-JPで多用）

### html
```
[[html]]
<div>…</div>
<script>…</script>
[[/html]]
```
- 実体は**別ドメインの iframe**。中の HTML は独立ページ。
- 中身は Wiki 構文としてパースされない。
- `<html>` / `<body>` そのものへのスタイル適用は不可。全体を `<div style="…">` で包む。
- **iframe の高さは中身の高さに自動追従する**。ただし中に `<iframe>` を入れるとその高さは計測されず 150px 固定になる。
- HTMLブロックにも固有URLがある（右クリック→このフレームのみ表示、で確認可能）。

### embed / embedvideo / embedaudio
```
[[embed]] <script src="…"></script> [[/embed]]
[[embedvideo]] <iframe src="//www.youtube.com/embed/XXX"></iframe> [[/embedvideo]]
[[embedaudio]] … [[/embedaudio]]
```
`[[embedaudio]]` の公式サンプルは Flash 前提で**現在は死んでいる**。音声/動画は SCP系なら `[[include :snippets:html5player |type=audio|url=…]]` を使う。

### iframe
```
[[iframe URL frameborder="0" scrolling="no" width="100%" height="200px" style="…" class="…" align="left"]]
```
許可属性は `frameborder`(0/1) / `align` / `height` / `width` / `scrolling`(yes/no) / `class` / `style` のみ。

## 21. div / span と `_` 変種

```
[[div class="x" id="y" style="…" data-foo="bar"]] … [[/div]]
[[div_ ]] … [[/div]]        前後の空白を切り詰め、余計な <p> 改行を作らない
[[span_ ]] … [[/span]]
[[a_ href="…"]] … [[/a]]
[[ul_]] / [[ol_]]
```
- `[[div]]` / `[[/div]]` は単独行に置くこと（さもないと認識されない）
- ネスト可
- **`[[/div]]` は「それより上に対応する `[[div]]` があれば」閉じられる**。この緩さがバグ利用技の土台になる。

ブロック配置:
```
[[<]] … [[/<]]     左寄せ
[[>]] … [[/>]]     右寄せ
[[=]] … [[/=]]     中央
[[==]] … [[/==]]   両端揃え
= 一行だけ中央寄せ
```
※ これらのタグは行末に**スペースすら置いてはいけない**。

## 22. ボタン・ソーシャル・ユーザー

```
[[button edit]] [[button source]] [[button print]] …
```
type: `edit, edit-append, edit-sections, history, print, files, tags, source, backlinks, talk, delete, rename, site-tools, edit-meta, watchers, parent, lock-page`
属性: `text` / `class` / `style`

```
[[button set-tags +tag1 -tag2 text="タグ変更"]]
```
`+tag` 追加 / `-tag` 削除 / `-*` 可視タグ全削除 / `-_*` 隠しタグ全削除。削除が追加より先に処理される。押下後ページがリロードされるので iftags と組み合わせられる。

```
[[social]]                                       全サービス
[[social digg,furl,del.icio.us,facebook]]
[[user ユーザー名]]        アイコンなし
[[*user ユーザー名]]       アイコンあり
```

## 23. エスケープ・コメント

| 記法 | 用途 |
|---|---|
| `@@ … @@` | 中身を一切パースしない（リテラル） |
| `@< … >@` | HTML エンティティを直接出力（`&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;` に置換して書く）。`@<&nbsp;>@` `@<&copy;>@` `@<&#252;>@` |
| `[!-- … --]` | ソース上のコメント。出力されない |
| `@@====@@` または `==== `（末尾スペース） | `====` セクション区切りのエスケープ。code ブロック内では末尾スペース方式のみ有効 |
| ` [[include …]]`（行頭スペース） | include のパースを止める |

## 24. タイポグラフィ

```
``引用''      →  “引用”
`引用'        →  ‘引用’
,,引用''      →  „引用”
<<引用>>      →  «引用»
>>引用<<      →  »引用«
dots...       →  …
em -- dash    →  em — dash （前後にスペース必須）
```

## 25. 式構文（公式だがほぼ知られていない）

一次情報: `www.wikidot.com/doc:expressions`

```
[[#if 値 | 真のとき | 偽のとき ]]
[[#ifexpr 式 | 真のとき | 偽のとき ]]
[[#expr 式 ]]
```
- 偽と判定されるのは `false` / `null` / 空文字 / `0` の4つのみ。それ以外は真。
- 使える関数は `abs`, `min`, `max` の3つだけ。
- **式は最大256文字**。
- `[[include]]` の `{$var}` と組み合わせるとコンポーネントに条件分岐を実装できる（SCP系コンポーネントの実装パターン）。

```
[[#expr 2*4/12-4+66%2 ]]
[[#ifexpr 2*4/12-4+66%2 < -3.5 | 小さい | 大きい ]]
[[#ifexpr 10 > {$num} | + | - ]]
```

## 26. 行頭必須タグ一覧（単独行に置かないと壊れるもの）

`[[div]]` `[[/div]]` `[[collapsible]]` `[[/collapsible]]` `[[gallery]]` `[[code]]` `[[/code]]`
`[[html]]` `[[/html]]` `[[note]]` `[[/note]]` `[[<]]` `[[>]]` `[[=]]` `[[==]]` とその閉じタグ
`[[include]]`（前後に改行）
