# 06 — 難解構文・バグ利用技 完全版

一次情報: `scp-jp.wikidot.com/esoteric-syntax` / `shitake-crude-production.wikidot.com`（皆の構文広場・ランダム技術・基礎研究室・モジュール仕様書・extension/javascript/csslab 各カテゴリ）/ `scp-wiki.wikidot.com/advanced-formatting-and-you`

これらは**Wikidotのパーサ順序・判定の甘さ・DOM実装**に依存している。仕様ではないので壊れる可能性がある。

---

## A. パーサ順序を突く技

### A-1. `%%content{0}%%` によるモジュール内 HTML/CSS 注入 ★最重要

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「応用編2」の章（CSSモジュール／htmlブロックへの値挿入） — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

公式仕様では **ListPages / ListUsers の本文に `[[html]]` や `[[code]]` を入れるとモジュールごと動作しない**。
しかし `%%content{0}%%` をタグ名の途中に挟むと回避できる。

```
[[module ListPages range="." separate="yes"]]
[[%%content{0}%%html]]
<script>
  var rating = %%rating%%;
  var updated = "%%updated_at%%";
</script>
<div id="x"></div>
[[/html]]
[[/module]]
```
```
[[module ListPages limit="@URL|0" range="." urlAttrPrefix="pageN"]]
[[%%content{0}%%module css]]
#page-title { font-size: %%limit%%% !important; }
[[%%content{0}%%/module]]
[[/module]]
```

**原理**: モジュール本文を検査する段階では `[[%%content{0}%%html]]` は `[[html]]` として認識されない。変数展開で `%%content{0}%%` が空文字に消え、その後のパスで初めて `[[html]]` が完成する。

**制約**
- `separate="yes"` が必須（`no` だとコンパイル単位が変わって成立しない）
- 複数ページがヒットするとヒット数だけHTMLブロックが生成される。1つに集約するには iframe 間通信が必要
- HTMLブロックに渡せるのは**文字列としての Wiki 構文**なので、JS 側で整形が必要
  （例: `%%updated_at%%` は `%%date|1234567890%%` のような文字列で来るので正規表現で数値を抜く）

**用途**: 評価値によるページ変化、最終更新からの経過時間表示、URLパラメータでレイアウトを可変にする、著者名の自動埋め込みなど。

### A-2. `%%変数%%` を分割してリテラル表示する

> 原典: 未特定（章冒頭の一次情報を参照）

`%%content{0}%%` を文書中にそのまま書きたいとき:
```
%%con%%content{0}%%tent%%
```
未定義変数はそのまま残るので、表示は `%%content{0}%%` になる。`%%ti%%` `%%tle%%` `%%da%%` 等も同じ用途で使われている。

### A-3. `[!-- --]` で隠したセクションを `%%content{n}%%` で取り出す ★

> 原典: 未特定（章冒頭の一次情報を参照）

`====` によるセクション分割は**ソース段階**で行われるが、`[!-- … --]` によるコメントは**レンダリング段階**で消える。したがって:

```
[[module ListPages offset="@URL|0" range="."]]
%%content{2}%%
[[/module]]
[[module ListPages limit="@URL|0" range="." urlAttrPrefix="page2"]]
%%content{3}%%
[[/module]]
[!--
====
これはページ1の内容（直接は表示されない）
====
これはページ2の内容
--]
```
直接ページを開くと `[!-- --]` の中身は表示されず、`%%content{n}%%` 経由でのみ現れる。

### A-4. `limit="@URL|0"` によるトグル

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「ページ変更ギミックの単一ページ化」の章 — 考案: physicslike 氏、寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

ListPages に `limit="@URL|0"` を与えると、**URLに値が無ければ 0 件＝何も出力されない**。URL に `/pageN_limit/1` を付けると1件だけ出力される。
`urlAttrPrefix` で名前空間を分ければ、1ページの中に任意個数の「隠しページ」を持てる。

```
通常          http://site.wikidot.com/page
ページ2       http://site.wikidot.com/page/offset/1/page2_limit/1
ページ3       http://site.wikidot.com/page/offset/1/page3_limit/1
```
`offset/1` は「元のページ本体（`offset="@URL|0"` のモジュール）を消す」ために使う。
これが **SCP-2998 / SCP-1111-JP 型のページ変更ギミックの単一ページ版**（physicslike 氏考案）。従来は子ページを複数作る必要があり、サンドボックスでテストできなかった。

### A-5. `====` を跨いだ CSS セレクタ分割 ★

> 原典: 未特定（章冒頭の一次情報を参照）

`%%content{1}%%%%content{2}%%` のように**セクションを連結**することを利用して、連結時にだけ意味を持つコードを書く。

```
[[module css]]
.PageChangeSect
====
ion1 {
display:none;
}
[[/module]]
====
[[module ListPages limit="@URL|0" range="." urlAttrPrefix="page2"]]
%%content{1}%%%%content{2}%%%%content{4}%%
[[/module]]
```
- 通常表示では section1 が見える（CSS が分断されていて無効）
- `page2_limit/1` を付けると content{1}+content{2} が連結して `.PageChangeSection1 { display:none; }` が成立し、section1 が消えて content{4} が現れる

### A-6. 「未閉鎖コメント」による条件ブロック（Colmod の実装）

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「Colmod - 多重折り畳み」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

```
[!-- {$coltop}-]
[[include :shitake{$coltop}crude-production:component:colmod
coltopbase=- | … ]]
[!-- {$coltopbase}-]
   （coltop としての中身）
[!-- {$colend}-]
   （colend としての中身）
[!-- --]
```
- 引数が渡されなければ `{$coltop}` は文字列のまま残り、`[!-- {$coltop}-]` はコメントが閉じないので後続を丸ごと飲み込む
- `coltop=-` を渡すと `[!-- --]` が成立してコメントが閉じ、その先が有効になる
- 同時に `:shitake{$coltop}crude-production:` が正しいサイト名 `:shitake-crude-production:` に化ける

**1ページが引数によって coltop にも colend にもなる**という実装。`[[#if]]` と併用されている。

### A-7. tabview に「フッター」を付ける

> 原典: [折り畳みタブの諸所](http://shitake-crude-production.wikidot.com/customtabview) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[tabview]]
[[tab]]内容1[[/tab]]
[[tab]]内容2[[/tab]]
フッター（常に表示される）
[[div style="display:none;"]]
[[/tab]]
[[/tabview]]
[[/div]]
```
**原理**: `[[/tabview]]` の直前に `[[/tab]]` が無いと構文エラーになるが、**対応する `[[tab]]` が存在しなくても判定は通る**。そこで余分な `[[/tab]]` を置き、それを `display:none` の div で隠す。
末尾の `[[/div]]` は必須（`[[/div]]` は「それより上に対応する `[[div]]` があれば」閉じられるという緩い判定を利用している）。無くても一見動くが DOM が壊れる。

### A-8. 深層インクルード（インクルード引数のデフォルト値）

> 原典: 未特定（章冒頭の一次情報を参照）

```
[[include sample-include
|sentence = {$sentence}
|sentence = undefined
]]
```
同名引数を2回書くと、**下の定義が先に解決され、上の `{$sentence}` がそれを受け取る**。呼び出し側が値を渡せば上書きされる。
Wikidot の公式コンポーネントはほぼ全部この「ハブ用インクルードページを1枚挟む」パターンでデフォルト値を実装している。

```
component:coltop  →  component:coltop-deep  を既定値付きで呼ぶだけのページ
```

### A-9. `[[iftags]]` をタグの属性欄に埋め込む

> 原典: 未特定（章冒頭の一次情報を参照）

```
[[div_ class="rateBox" [[iftags +殿堂入り]]style="display:none;"[[/iftags]]]]
[[image logo.png link="[[iftags +en]]heritage-collection-arc[[/iftags]][[iftags +jp]]heritage-collection-jp[[/iftags]]"]]
[[div class="modalbox [[iftags +殿堂入り]]heritage[[/iftags]]"]]
```
タグ属性の中に別のタグを書ける。SCP-JP のクレジットモジュールが多用している。

### A-10. `[[include]]` は `[[code]]` の中でもパースされる

> 出典: Wikidot 公式仕様

公式仕様。回避は行頭に半角スペース1つ。
コピペ用サンプルコードを書くときの定番の落とし穴。

---

## B. CSS だけで動くギミック（JavaScript 不要）

### B-1. `:target` による表示切替 ★

> 原典: [ターゲットによる文章切替](http://shitake-crude-production.wikidot.com/targeting-sentence-change) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[module css]]
#u-collapsible .unfolded,
#u-collapsible:target .folded { display:none; }
#u-collapsible:target .unfolded,
#u-collapsible .folded { display:block; }
[[/module]]

[[div id="u-collapsible"]]
[[div class="folded"]]変更前[[/div]]
[[div class="unfolded"]]変更後[[/div]]
[[/div]]

[#u-collapsible これを押すと文章が変わる]
```

兄弟セレクタ版（本文の途中の語句だけを差し替える）:
```
[[module css]]
#u-change { display:none; }
#u-change ~ .changearea .a,
#u-change:target ~ .changearea .b { display:inline; }
#u-change:target ~ .changearea .a,
#u-change ~ .changearea .b { display:none; }
[[/module]]

[[div id="u-change"]][[/div]]
[[div class="changearea"]]
説明: … [[span class="a"]]実験開始前[[/span]][[span class="b"]]実験開始後[[/span]] …
[#u-change 実験開始]
[[a href="#u-change" class="a"]]実験開始（押すと消える）[[/a]]
[[/div]]
[[/module]]
```
- ユーザー定義 id には `u-` が自動付与されるので、CSS も参照も `u-` 込みで書く
- SCP-JP のクレジットモーダル（`#u-credit-view`）も同じ仕組み

### B-2. 遠隔折り畳み（Remote Collapsible）★

> 原典: [遠隔折り畳み要素](http://shitake-crude-production.wikidot.com/remote-ctrl-collapsible) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

Wikidot の collapsible は jQuery で `.collapsible-block-folded` / `.collapsible-block-unfolded` を show/hide しているだけ。**このクラスを手書きすると、折り畳みの外にある要素も一緒に開閉できる**。

```
[[module css]]
.remoteCollapsible > .collapsible-block > .collapsible-block-unfolded { display:block !important; }
.remoteCollapsible > .collapsible-block > .collapsible-block-unfolded > .collapsible-block-content { opacity:1 !important; }
.remoteCollapsible .collapsible-block-unfolded[style="display:none"] > .collapsible-block-unfolded-link { display:none; }
.remoteCollapsible .collapsible-block-unfolded[style="display: none;"] > .collapsible-block-unfolded-link { display:none; }
.remoteCollapsible .collapsible-block-unfolded .hide-show { display:none; }
[[/module]]

[[div class="remoteCollapsible"]]
[[collapsible show="+ 開く" hide="- 閉じる"]]
最初から表示されている文章
[[div class="collapsible-block-unfolded" style="display:none"]]
開いたときだけ出る文章
[[/div]]
[[div class="collapsible-block-folded"]]
閉じているときだけ出る文章
[[/div]]
[[/collapsible]]
[[/div]]
```
- 1つのボタンで複数箇所を同時に切り替えられる
- `collapsible-block-unfolded` の中に `collapsible-block-content` を入れるとフェードインが付く

### B-3. サインイン / 非サインインで文面を切り替える ★

> 原典: [サインインユーザと非サインユーザに対する文章表示切替](http://shitake-crude-production.wikidot.com/sitemember-textchanger) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

`[[module ListUsers users="."]]` は匿名ユーザーに対して**HTMLを生成しない**。これと `:nth-child` を組み合わせる。

```
[[module css]]
.textchange div.sitemember:nth-child(2) { display:none; }
[[/module]]

[[div class="textchange"]]
[[module ListUsers users="."]]
[[div class="sitemember"]]ようこそ %%name%% さん！[[/div]]
[[/module]]
[[div class="sitemember"]]ようこそゲストさん！[[/div]]
[[/div]]続きの文章
```
- サインイン時は `.sitemember` が2個生成され、2番目（ゲスト用）が CSS で消える
- 非サインイン時は1個しか無いので、そのまま表示される
- `[[div class="textchange"]]` の中に他の div を置くと `:nth-child` がずれる
- `[[/div]]` の直後は改行せずに続きの文章を書く（余分な改行が入るため）

### B-4. 閲覧者のアイコンを表示する

> 原典: [閲覧ユーザのアイコンを出す方法](http://shitake-crude-production.wikidot.com/show-your-icon) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[module ListUsers users="."]]
[[image http://www.wikidot.com/avatar.php?userid=%%number%%]]
[[/module]]
```
`%%number%%` は Wikidot のユーザーID。`avatar.php?userid=<ID>` がアバター画像のURL。
「報告書を書いた人物が閲覧者自身になる」といった演出に使われる。

### B-5. 評価値による表示変化

> 原典: [rate数による表示](http://shitake-crude-production.wikidot.com/everyonerate:ratechangemodule) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

A-1 と組み合わせて `%%rating%%` を JS に流し込む。
ページを開いた**時点**の値なので、投票直後には反映されない（リロードが必要）。

### B-6. FontAwesome

> 原典: [FontAwesome応用編](http://shitake-crude-production.wikidot.com/font-awesome-step-up) / [HTMLブロック内でfontawesomeを使う](http://shitake-crude-production.wikidot.com/use-font-awesome) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

サイトテーマに含まれているので、本文では素で使える。
```
[[span class="fa-stack fa-lg"]][[span class="fa fa-handshake-o fa-stack-1x"]]@<&nbsp;>@[[/span]][[span class="fa fa-ban fa-stack-2x"]]@<&nbsp;>@[[/span]][[/span]]
```
中身が空だと消えるので `@<&nbsp;>@` を入れる。
HTMLブロック内では別ドメインなので、`<style>@import url(…sigma-9…/style.css)</style>` などでCSSを持ち込む必要がある。

### B-7. ノイズテキスト（data属性の利用）

> 原典: [ノイズテキストCSSの紹介](http://shitake-crude-production.wikidot.com/noise-text-animation) — C-take 著, CC BY-SA 3.0（本稿は要約・再構成）。CSS実装のベースは Lucas Bebber "CSS Glitched Text"（MIT License）の第三者コード。

**Wikidot の div/span は `data-*` 属性を受け付ける**。これを CSS の `content: attr(data-text)` で使う。
```
[[div class="glitch-b" data-text="HELP"]]HELP[[/div]]
```
`::before` / `::after` に同じ文字を位置ずらしで描画し、`clip` をアニメーションさせる。
- 親要素のテキストと `data-text` は同一にする
- 疑似要素に背景色を敷いて親の文字を隠す必要がある
- 仕様上ノイズは1行目にしかかからない
（原典: Lucas Bebber "CSS Glitched Text", MIT）

### B-8. CSS Filter

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「CSS Filterの入門」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

```
[[image URL style="filter: grayscale(100%);"]]
[[image URL style="filter: hue-rotate(125deg);"]]
[[image URL style="filter: sepia(100%) hue-rotate(125deg);"]]
```
空白区切りで合成。画像に限らず CSS が当たる全要素（サイドバー、画面全体）に適用できる。

### B-9. 脚注ハック

> 原典: [脚注の諸所](http://shitake-crude-production.wikidot.com/footnote-explain) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

| やりたいこと | 方法 |
|---|---|
| スマホでの強制スクロールを防ぐ | `[[collapsible show="脚注" hide="脚注を閉じる" hideLocation="bottom"]][[footnoteblock]][[/collapsible]]` |
| 脚注一覧を消す | `.footnotes-footer { display:none; }` または `[[size 0%]][[footnoteblock]][[/size]]` |
| 位置とタイトルを変える | `[[footnoteblock title="…"]]` を置きたい場所に |
| 脚注に画像を入れる | `[[footnote]][[image …]][[/footnote]]` |
| ホバー時だけ画像を出す | 上記＋ `.footnote-footer img { display:none; }` |
| ホバーウィンドウの色 | `.hovertip { border: … !important; }` / `.hovertip .content { background-color:#000; color:#fff; }` |
DOM: `div.footnotes-footer > div.title` ＋ `div.footnote-footer#footnote-N`（N は脚注番号と一致）。

### B-10. ページタイトルの差し替え・移動・クリック切替

> 原典: [タイトル位置変更及び機能増加](http://shitake-crude-production.wikidot.com/title-powerup) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[module CSS]]
#page-title { display: none; }
.fake_title { font-size:200%; color:#990011; border-bottom:1px solid #bbb; }
.fake_title p { margin:0; padding:0; }
[[/module]]
[[module ListPages separate="no" limit="1" range="."]]
[[div class="fake_title"]]
%%title%%
[[/module]]
[[/div]]
```
`[[div]]` の開始をモジュール内、終了をモジュール外に置いても通る（A-7 と同じ緩い判定）。
`[[collapsible show="%%title%%" hide="別のタイトル"]]` にすればタイトルをクリックで変えられる。

### B-11. 評価モジュールの改造

> 原典: [評価モジュールとしてダメな評価モジュール](http://shitake-crude-production.wikidot.com/not-use-this-is-a-bad-rate-module) / [お前が評価すべきもの](http://shitake-crude-production.wikidot.com/myrating-point-name) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[module css]]
.page-rate-widget-box .rate-points:before { content:"胸毛 : "; }
.page-rate-widget-box .rate-points { font-size:0; }
.page-rate-widget-box .rate-points > .number { font-size:12px; }
.page-rate-widget-box .rateup, .page-rate-widget-box .ratedown, .page-rate-widget-box .cancel { … }
[[/module]]
```
※ SCP 本サイトでは評価モジュールの破壊はポリシー違反。表示名の変更程度に留めること。

### B-12. 偽りの認証（fakeprot）

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「偽りの認証」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

```
[[include :scp-jp:component:fakeprot |name=Site:8192 Director Y.Gineri]]
[[div class="collapsiblealt"]]
[[collapsible show="認証" hide="ログアウト"]]
…
[[/collapsible]]
[[/div]]
```
中身は `[[module MailForm]]` に**矛盾したバリデーション**（`maxLength:10` と `minLength:100`）を与えて絶対に送信できなくしたもの。パスワード欄は `text-security: disc` で伏字にしている。実際の開閉は普通の collapsible。

### B-13. `<details>` を使った折り畳み

> 出典: HTML 標準（<details> 要素）

HTMLブロック内なら素の HTML が使える。`summary` 内に色付き span を入れられるなど、Wikidot の collapsible より自由。
```
[[html]]
<details><summary>前<span style="color:red">赤字</span>後</summary><p>本文</p></details>
[[/html]]
```

---

## C. HTMLブロック / iframe を巡る技

### C-1. HTMLブロックの正体

> 原典: 未特定（章冒頭の一次情報を参照）

- 実体は**別ドメインの iframe**。親ページの DOM/CSS には触れられない
- 高さは**中身の高さに自動追従する**
- ただし **中に `<iframe>` を入れるとその高さは計測されず、150px に固定される**（実験で確認済み）
- 相対パス `./` で同一ページの添付ファイルを参照できる
- `body { padding:0; margin:0; }` を入れて余白を潰すのが定石

### C-2. iframe 間通信（postMessage）

> 原典: C-take 氏「基礎研究室」（`shitake-crude-production.wikidot.com` の basestudy 系ページ。具体ページ未特定）— 実測データの引用, CC BY-SA 3.0。

```javascript
var frames = window.parent.window.frames;   // 兄弟フレームの配列
frames[1].postMessage(data, "*");
window.addEventListener("message", function(e){ … });
```
実測データ（C-take 氏の基礎研究室）:
| 状態 | Chrome | Edge | Firefox |
|---|---|---|---|
| サインイン | 成功 | 成功 | 成功 |
| サインアウト | 成功 | 失敗 | 失敗 |

さらに `window.parent.window.frames.length` は**サインイン時2・サインアウト時5**。つまり**サインアウト時は未知の iframe が3つ挿入される**（Edge/Firefox ではページ先頭に入るため、フレーム番号が1ずれる）。フレーム番号の決め打ちは危険で、自分のインデックスを探索するコードが必要。

### C-3. 名前付き iframe で値を渡す

> 原典: 未特定（章冒頭の一次情報を参照）

```
[[module ListUsers users="."]]
[[embed]]
<iframe src="http://…/sitemember-textchanger/code/1#%%title%%" name="userName" style="display:none;"></iframe>
[[/embed]]
[[/module]]
```
- `[[embed]]` を使うと任意の `<iframe>` を置ける（`[[iframe]]` は属性が限定されている）
- `name="userName"` により `window.parent.window.userName` でアクセスできる
- ハッシュ（`#%%title%%`）でユーザー名を運ぶ
- 受け側では `try { window.parent.window.userName } catch(e) { /* 非サインイン */ }` で分岐

### C-4. iframe の高さ自動調整

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「任意のタイミングでHTMLブロックをリサイズ！」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

`[[html]]` を使わず素の `[[iframe]]` にしたい場合（`[[html]]` の中の iframe は高さが取れないため）:
- 内側の HTML の末尾に `<div id="iframeset"></div>` を置く
- その要素の `getBoundingClientRect().top` を高さとみなす
- 高さが変わるたび `…/common--javascript/resize-iframe.html?<乱数>#<高さ><パス>` を読み込む隠し iframe を作り、親に通知する
- 親側は `[[iframe URL class="html-block-iframe" allowtransparency="true" style="height: 0px;" frameborder="0" scrolling="no"]]`
- **同一 URL に対して2つ以上の自動調整 iframe を置くとバグる**

### C-5. コードブロックを CDN 配信に使う

> 原典: 未特定（章冒頭の一次情報を参照）

```
<script src="http://site.wikidot.com/page-name/code/1"></script>
[[module css]] @import url('/page-name/code/1'); [[/module]]
[[iframe http://site.wdfiles.com/local--code/page-name/2#hash class="html-block-iframe"]]
```
- `…/code/N` はページソースの N 番目のコードブロックの生データ
- `…/code_/N` は `_template` 適用後
- `wdfiles.com/local--code/<URLエンコードしたフルネーム>/N` はCDN経由（**アンチウイルスに弾かれにくい**という実務上の理由でこちらが推奨されている場面がある）
- Wikidot を JS/CSS のホスティングとして使える

### C-6. 動画に見える画像ブロック（SCP-895 / SCP-845 型）

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「動画っぽい動画じゃない何かの作り方」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

動画や GIF を使わず、HTML+CSS+JS を添付して iframe で読み込む。
```
[[div class="scp-image-block" style="width:300px;"]]
[[iframe 作品のURL style="width:300px; height:300px;" frameborder="0" scrolling="no"]]
[[div class="scp-image-caption" style="width:300px;"]]キャプション[[/div]]
[[/div]]
```
設計指針（原文の要点）:
- **高さは必ず固定**。ブラウザは横幅の計算は正確だが縦は頻繁に誤る（特に CSS 縦書き）
- 動画/GIFは重く、タイムスタンプを打てず、実行時に変化させられない。JS 生成なら軽くて可変
- Flash は不可。HTML5 Canvas を使う
- ライセンス: 素材は CC BY-SA 3.0 互換、コードは MIT 等。CodePen のパブリック作品は MIT

### C-7. 音楽を流す

> 原典: [音楽を流す](http://shitake-crude-production.wikidot.com/audioplay) — C-take 著, CC BY-SA 3.0。本稿は要約・再構成。

```
[[html]]<audio autoplay><source src="…mp3" type="audio/mpeg"></audio>[[/html]]
```
ループさせるなら `new Audio()` ＋ `canplaythrough` で `loop=true`。
本サイトでは `[[include :snippets:html5player |type=audio|url=…]]` を使い、autoplay は非推奨。

---

## D. 演出系コンポーネント（esoteric-syntax）

### D-1. 記事の中にフォーラム

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「記事の中にフォーラムを！」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

`[[include :scp-jp:component:addspecialcss]]` を前提に:
- `[[div class="DummyForumTitle"]]` … タイトル＋カテゴリ（箇条書きがカテゴリになる）
- `[[include :scp-jp:component:pseudosummary |URL=|NAME=|DATE=|POST=|SUMMARY=block\|none]]` ＋ `component:pseudosummary-end`
- `[[include :scp-jp:component:pseudopost |URL=|NAME=|DATE=|TITLE=]]` … **末尾に `[[/div]]` が2つ必要**。返信はその2つの `[[/div]]` の間にネストする
- `[[div class="DummyNew-post"]][[span class="fake-link"]]新しくコメントを投稿する[[/span]][[/div]]`
- 日付はイギリス式（`2 Apr 2017 12:08`）、月は英語3文字
- `[[/div]]` の数で必ず混乱するので `[!-- コメント1 Start --]` 等でマーキングする

### D-2. カスタムタブレイアウト

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「折り畳みタブ・レイアウト変更」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

`addspecialcss` 導入後、`[[div class="CustomTabRJ"]]` / `CustomTabRJC`（色違い）で `[[tabview]]` を囲む。
IE/Edge ではタブの高さが固定される（意図的仕様）。タブ名は短くすること。

### D-3. 星空と UFO（2017年エイプリルフール）

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「星空とUFO」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

```
[[module CSS]] @import url(…/SCP-stars_3.css); [[/module]]        星空（全面）
[[module CSS]] @import url(…/SCP-1010CSS6.css); [[/module]]        UFO
[[module CSS]] @import url(…/BasicNightBackScreen6.css); [[/module]] 任意の場所に置く用
```
```
[[div class="nightskyScreen" style="width:90%;height:200px;margin:auto;color:#FFF;"]]
[[div class="starBackScreen"]][[/div]]
[[div class="starBackScreen2"]][[/div]]
[[div class="starBackScreen3"]][[/div]]
[[div class="ufo"]][[/div]]
[[/div]]
```
UFO は軌道の都合で height 150px 以上が必要。
実装は `#container-wrap-wrap` / `#container-wrap` / `#container` の `::before` `::after` と `#skrollr-body::after` を占有し、`#page-content` `#side-bar .side-block` `#footer` に `z-index:3` を与える。

### D-4. HTMLブロック拡張（レガシー）

> 原典: [難解Wikidot構文](http://scp-jp.wikidot.com/esoteric-syntax)「htmlブロックを拡張しよう！」の章 — 寄稿者 13 名（ページ履歴参照）, CC BY-SA 3.0。本稿は要約・再構成。

`scpHTMLblockCtrl_ver1_ex.js` ＋ `scp-WikidotCss.css` をHTMLブロックに読み込むと、iframe 内で `<collapsible>` `<blockquote>` 相当が書け、`<div id="scpHTMLblockResizeSwitch">` で高さ補正が効く。
- 折り畳みの中に入れるときだけ `isHTMLblockHide = true;` を追加（さもないと無駄な監視ループが回り続ける）
- 任意タイミングの再計算は `correctIframeSize()`
- 予約グローバル名が15個以上ある（`scpCreateCollapsible`, `correctIframeSize`, `ParentCollasible` クラス, `scpCollasibleLink+数字` id など）
- **本文の脚注に「現在の Chrome はこの章で扱う問題を克服した。よってこの技術はレガシー」と明記されている**

---

## E. 小ネタ集

| 技 | 内容 |
|---|---|
| `@@ @@` / `@@@@` | 何も表示しない要素。div 間の隙間、空行の確保 |
| `[[div_]]` | 余計な `<p>` を作らない div。コンポーネント実装では必須 |
| `[[table class="wiki-content-table"]]` | 簡易テーブルと同じ見た目のまま `colspan`/`rowspan`/セル内改行/幅指定ができる |
| `[[cell style="width:9em;"]]` | 長文セルに潰される問題の回避 |
| `[[table style="display:block;float:right;"]]` | 表の右寄せ |
| `#content-wrap { min-height: … }` | 文字数の少ない記事でフッターが上がるのを防ぐ |
| `#show-upload-button::after { content:"…" }` | サイト全体への注意書き挿入（100KB制限の告知に使われた） |
| `.menu-item img[src$="series.png"]` | 属性セレクタでサイドバーのアイコンを差し替える |
| 奇声言語 | オリジナル BrainFuck を実装するライブラリ（`hoby:kisei`） |
| 時限式移動 | 時間経過でページ遷移する JS ライブラリ（`time-move`、`…/time-move/code/1` を script src に） |

> 原典（この表のうち原典が判明しているもの）: [奇声言語](http://shitake-crude-production.wikidot.com/hoby:kisei) / [時限式移動](http://shitake-crude-production.wikidot.com/time-move) — いずれも C-take 著, CC BY-SA 3.0。本稿は要約・再構成。他の行は Wikidot の一般的な構文・CSS の利用法。

---

## F. この章の技を使うときの心得

1. **すべて仕様外**。Wikidot 側の変更で壊れる。重要な記事では冗長性を持たせる。
2. **サンドボックス3で必ず検証する**。子ページ依存のギミックは単一ページ版（A-4）にしておくと検証しやすい。
3. **ナビゲーション・評価モジュール・翻訳モジュールを壊さない**（CSSポリシー違反）。
4. **モバイルで確認する**。SCP をスマホで読む読者は多い。
5. ライセンス（CC BY-SA 3.0 互換、コードは MIT 等）と出典表記を守る。
6. 大掛かりなものはテクニカルスタッフに相談する。
