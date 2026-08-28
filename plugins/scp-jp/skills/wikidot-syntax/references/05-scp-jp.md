# 05 — SCP財団固有の拡張（JP / EN）

一次情報: `scp-jp.wikidot.com/how-to-write:format`, `wiki-syntax`, `japanese-syntax`, `component:jstyles`, `credit:start/end`, `component:image-block(-base)`, `anomaly-classification-system-guide`, `theme:black-highlighter-theme`, `custom-theme-policy` / `scp-wiki.wikidot.com/wiki-syntax`, `advanced-formatting-and-you`, `css-policy`

---

## 1. SCP-JP の必須事項

### クレジット付き評価モジュール（義務）

> 参照: [credit:start](http://scp-jp.wikidot.com/credit:start) / [credit:end](http://scp-jp.wikidot.com/credit:end)（実装本体）

通常の `[[module Rate]]` 単独は**現在ルール上使用禁止**。以下に一本化されている。

```
[[include :scp-jp:credit:start]]
**タイトル:** SCP-XXX-JP - タイトル
**著者:** [[*user あなたのアカウント名]]
**作成年:** 20XX
[[include :scp-jp:credit:end]]
```
- `credit:start` の実装は `[[div_]]` の塊 ＋ `[[module Rate]]` ＋ `#u-credit-view` へのアンカーリンク（`:target` でモーダルを開く）
- CSS は `local--code_/credit%3Astyle/1` を `@import`
- `[[iftags +殿堂入り]]` で殿堂入りエンブレム版に自動で切り替わる（**タグ条件を div のタグ属性欄に埋め込む**書き方、→ 06）
- 翻訳・プレビュー用に `credit:start-preview` / `credit:end-preview`、レート無しは `[[include credit:start |mode=no-rate]]`

### 画像

> 参照: [component:image-block](http://scp-jp.wikidot.com/component:image-block)（実体: [component:image-block-base](http://scp-jp.wikidot.com/component:image-block-base)）

```
[[include :scp-jp:component:image-block
name=画像URL|
caption=説明|
width=350px|
link=http://example.com|
align=right|
clear=true]]
```
実体は `component:image-block-base`。生成物は `.scp-image-block.block-{align}` ＋ `.scp-image-caption`。
`[[iftags 画像差し止め]]` が入っており、そのタグを付けると自動で「noimage」画像に差し替わる。
EN 版は `alt=alt` / `alt-text=…` の指定に対応（代替テキストが無いときは `alt=alt` を書かない）。

画像はファイルストレージ（`scp-jp-storage`）にアップロードし、ライセンスガイド・画像利用ポリシーに従うこと。**アップロードは 100KB 以下**という運用制限がある（サイト側に注意書きCSSが仕込まれている）。

### 音声・動画

> 参照: [snippets:html5player](http://snippets.wikidot.com/html5player) / [snippets:mp3](http://snippets.wikidot.com/mp3) / [component:audio-player](http://scp-jp.wikidot.com/component:audio-player)

```
[[include :snippets:html5player |type=audio|url=…]]     現行の推奨
[[include :snippets:mp3 |URL=…]]                        旧・MP3用
[[include component:audio-player |URL=…|autoplay=true]] 財団標準プレイヤー（autoplayは現在死んでいる）
```
Wikidot 公式の `[[embedaudio]]` は Flash 前提で機能しない。音声を付けた記事には `音声添付`(audio) タグを付ける。autoplay は非推奨。

---

## 2. jstyles（日本語表現用Wiki構文拡張スタイル）

> 参照: [component:jstyles](http://scp-jp.wikidot.com/component:jstyles)

```
[[include :scp-jp:component:jstyles]]
```
これ1行で以下が使えるようになる。

| 表現 | 構文 |
|---|---|
| ルビ | `{{漢字^^かんじ^^}}` |
| 圏点（ゴマ） | `{{,,テキスト,,}}` |
| 圏点（点） | `{{//テキスト//}}` |
| 圏点12種 | `[[span class="kenten-b\|c\|janome\|t\|goma\|wb\|wc\|doublec\|wt\|wgoma\|hoshi\|kane"]]…[[/span]]` |
| 傍線 | `[[span class="bousen"]]…[[/span]]` |
| 波線 | `__{{テキスト}}__` |
| くの字点 | `[[span class="henoji"]]` / `dhenoji`（濁点付き）/ `hdhenoji`（半濁点付き） |
| 割注 | `--{{前半}}{{後半}}--` |
| 縦書き | `[[div class="tategaki"]] … [[/div]]` |
| 縦書き詩 | `[[div class="vpoem"]] … [[/div]]` |
| 改稿マーカー | `[[div class="pseudo-tags"]]` 内で `##new\|新##` `##old\|旧##` |
| 偽装タグ | `[[div class="pseudo-tags"]]` ＋ 箇条書き |
| 等幅ビットマップ | `[[include :scp-jp:component:ayu18]]` ＋ `[[div class="monoayu"]]` |
| 神代文字 | `[[include :scp-jp:component:hotsu]]` ＋ `[[div class="hotsu"]]` |
| 外字 | `[[include component:gaiji \|name=nagi\|code=u237ff]]` ＋ `[[span class="nagi"]]〓[[/span]]` |

### 実装原理（重要）
jstyles は Wikidot が出力する既存タグを**再定義**している。

- `{{…}}` → `<tt>` を `display: inline-table; text-align:center; line-height:1; height:1em` にする
- `^^…^^` → `<sup>` を `display: table-header-group; font-size:0.6em` にする → **ルビ**になる
- `,,…,,` → `<sub>` に `text-emphasis-style: filled sesame` → **ゴマ圏点**
- `//…//` → `<em>` に `text-emphasis-style: filled dot` → **点圏点**
- `__…__` → `span[style="text-decoration: underline;"]` の中の `tt::before` に linear-gradient で**波線**
- `--…--` → `span[style="text-decoration: line-through;"]` を `inline-flex; flex-direction: column` にし、中の2つの `tt` を50%サイズで縦積み → **割注**

**帰結**: jstyles を入れると `{{teletype}}` は等幅表示ではなくなる。これは仕様であって不具合ではない。等幅が必要なら `component:ayu18` の `.monoayu` を使う。

- 外字は GlyphWiki のグリフ名（例 `u237ff`）を webfont 化して使う。`span` の中身はコピペ時に実際にコピーされる文字なので `〓` や読みを入れておく。
- **第三者素材のライセンス**（[component:ayu18](http://scp-jp.wikidot.com/component:ayu18) / [component:hotsu](http://scp-jp.wikidot.com/component:hotsu) 経由で導入するフォント）: ayu18 は public domain、神代文字は改変厳禁のフリーフォント、GlyphWiki はウェブフォント利用可。

---

## 3. コンポーネント（SCP-JP `component:` / `theme:`）

### esoteric-syntax 由来（ページ外観の改変）

> 参照: 各 `[[include]]` のページ名がそのまま `http://scp-jp.wikidot.com/component:<name>` の実装ページ（例: [component:changepagetitle](http://scp-jp.wikidot.com/component:changepagetitle)）。

```
[[include :scp-jp:component:changepagetitle | TITLE=SCP財団日本支部 | COLOR=#EEE]]
[[include :scp-jp:component:topsubtitle    | TITLE=SCP Foundation JP-branch | COLOR=#EEE]]
[[include :scp-jp:component:headsubtitle   | title=確保、収容、ナナフシ]]
[[include :scp-jp:component:changelogo     | IMAGE=https://…/logo.png]]
[[include :scp-jp:component:guruguru]]
[[include :scp-jp:component:changeguruguru | IMAGE=…]]   ※guruguru の後に置く
[[include :scp-jp:component:addspecialcss]]              疑似フォーラム/カスタムタブ用CSS
[[include :scp-jp:component:fakeprot | name=Site:8192 Director Y.Gineri]]
```
実装はいずれも `[[module CSS]]` 1枚。
- `changepagetitle` … `#html-body #header h1 a span { font-size:0 }` ＋ `h1 a::after { content: "{$TITLE}" }`
- `topsubtitle` … `h1 a::before`
- `headsubtitle` … `#header h2 span::before`
- `changelogo` … `#header { background-image: url(…) }`（`background` 一括指定はモバイル位置を壊すので不可）
- ロゴ画像は**正方形キャンバス**にすること

**技術ノート**: これらは `#header h1 a` の `::before` / `::after` を占有する。自作 CSS と併用するときは衝突に注意。

### 多重折り畳み Colmod

> 参照: [component:coltop](http://scp-jp.wikidot.com/component:coltop) / [component:colend](http://scp-jp.wikidot.com/component:colend)

`[[collapsible]]` はネストできない。代替：
```
[[include :scp-jp:component:coltop show=+ 開く|hide=- 閉じる]]
  [[include :scp-jp:component:coltop show=+ 開く|hide=- 閉じる]]
    何度でも
  [[include :scp-jp:component:colend nohide=true]]
[[include :scp-jp:component:colend nohide=true]]
```
| 再現したい collapsible | 書き方 |
|---|---|
| `hideLocation="both"` | `colend hide=△ 閉じる` |
| `hideLocation="bottom"` | `coltop nohide=true` ＋ `colend hide=- 閉じる` |
| `folded="no"` | `coltop folded=false` |
| 偽りの認証風 | `coltop ifprot=true` または `[[div class="collapsiblealt"]]` で囲む |

実装は `foldable-list-container`（CSS だけで開閉する `ul/li`）＋ `[[#if]]`。JavaScript を使わないのでネストできる。

### ACS（アノマリー分類システム）

> 参照: [component:anomaly-class-bar-source](http://scp-jp.wikidot.com/component:anomaly-class-bar-source) / [component:acs-hybrid-text-bar-source](http://scp-jp.wikidot.com/component:acs-hybrid-text-bar-source) / [component:acs-animation](http://scp-jp.wikidot.com/component:acs-animation)

```
[[include :scp-jp:component:anomaly-class-bar-source
|item-number= 2105
|clearance= 2
|container-class= euclid
|secondary-class= none
|disruption-class= vlam
|risk-class= notice
]]
```
ハイブリッド/テキスト版:
```
[[include :scp-jp:component:acs-hybrid-text-bar-source
|version= hybrid（または text）
|item-number= 2105
|clearance-level= 2
|containment-class= euclid
|include-secondary= yes
|secondary-class= apollyon
|secondary-icon= …svg
|disruption-class= vlam
|risk-class= notice
]]
```
アニメーション追加は `component:acs-animation`。
コンポーネントを使わない「ベアボーン」表記も正式：
```
**アイテム番号:** SCP-4205
**クリアランスLv2:** Restricted

**オブジェクトクラス:** Euclid
**撹乱クラス:** 2/Vlam
**リスククラス:** 1/Notice
```

### その他よく使うもの
- [component:license-box](http://scp-jp.wikidot.com/component:license-box) / [component:license-box-end](http://scp-jp.wikidot.com/component:license-box-end) … 出典表示ボックス
- [component:info-ayers](http://scp-jp.wikidot.com/component:info-ayers) … 情報バー
- [component:interwiki-style](http://scp-jp.wikidot.com/component:interwiki-style) … 翻訳モジュール(`.scpnet-interwiki-frame`)のスタイル。中身の改変・削除は禁止

---

## 4. テーマ

> 参照: [theme:black-highlighter-theme](http://scp-jp.wikidot.com/theme:black-highlighter-theme) / [component:bhl-dark-sidebar](http://scp-jp.wikidot.com/component:bhl-dark-sidebar) / [component:collapsible-sidebar](http://scp-jp.wikidot.com/component:collapsible-sidebar)

```
[[include :scp-jp:theme:black-highlighter-theme]]
[[include :scp-jp:component:bhl-dark-sidebar]]
[[include :scp-jp:component:collapsible-sidebar]]
```
Black Highlighter は CSS カスタムプロパティ（`--swatch-*`, `--gradient-header`, `--title-font`, `--UI-font`, `--mono-font` 等）を大量に定義しており、色や書体はこれらを上書きするだけで変えられる。JP版は `scp-jp.github.io/Black-Highlighter/` を `@import`。

GoI テーマの例（実験室に全ソースあり）: 第三法則、天へ、聖クリスティーナ学院、MC&D、放浪者の図書館、空想科学部門、ワンダーテインメント博士、アンダーソン・ロボティクス、太平洋司令部、リザレクション、ODSS、Nu-SCP、テクノブラスト、日本生類創研カタログ、シカゴ・スピリット、終焉の在り方 など。

---

## 5. CSS ポリシー（EN、JP もほぼ同等）

テーマを本サイトに投稿する際の制約。個別ページの埋め込み CSS にも大半が適用される。

- ライセンスは wiki と同じ CC BY-SA
- **ナビゲーション要素・評価モジュール・成人向け警告を削除/隠蔽/破壊してはならない**
- 翻訳モジュールはスタイル変更のみ可、中身の改変・削除は不可
- 主要ブラウザ（Chromium / Firefox / Safari）で正常動作し、モバイルでも破綻しないこと
- テーマは `theme:` カテゴリに置き、**利用者には `[[include]]` を案内すること。`@import` 方式を案内してはならない**
- 構文で HTTP リンクを使わせてはならない（HTTPS のみ）
- テーマページ自身にそのテーマを適用し、プレビューとして機能させること
- **Bloat code 禁止**（基準テーマ Sigma-10 からの丸コピーは不可）。`!important` は必要最小限
- **ホットリンク禁止**。画像・フォント等はテーマページに添付する（Google Fonts など明示的に許可されたサービスは例外）
- CSS はサンドボックスから読み込ませてはならない
- Tech Team の承認が必須。-10 票で削除対象になるのは通常記事と同じ

JP には `custom-theme-policy` / `custom-theme-jp` / `css-previewer` / `css-theme-preparation-tool` がある。

---

## 6. EN 側の追加事項

- `advanced-formatting-and-you`（DrMagnus）… div/CSS/iframe/ListPages の実践入門。「Options → View Page Source で他人の実装を全部読める」が最初の教え
- `SCP Style Resource`（S D Locke）… 各種ログ・フォーマットのコピペ用テンプレート集
- EN の引用ブロック代替 `[[div class="blockquote"]]` は JP でも有効
- 「タブの中にタブ」は素直な方法では不可。専用手法はあるが可読性の理由で非推奨とされている
