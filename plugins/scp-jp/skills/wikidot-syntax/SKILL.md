---
name: wikidot-syntax
description: Wikidot の Wiki 構文・モジュール・テンプレートと、SCP財団（SCP-JP / SCP-EN）固有の拡張構文・ギミック実装のリファレンス。Wikidot サイトのページやテーマを書く・直す作業、SCP 記事の執筆、`[[module ...]]` `[[include]]` `[[collapsible]]` 等を含む構文の質問で使う。Markdown とも MediaWiki とも異なる独自構文なので、記憶で書かず該当する reference を読んでから答える。
---

# Wikidot Syntax

Wikidot（SCP財団が使っているホスティングサービス）の構文リファレンス。
**Markdown でも MediaWiki でもない独自構文**であり、モジュール・テンプレート・URLパラメータ・CSSが密結合している。記憶で書かず、必ず該当 reference を読むこと。

## 使い方

まず何を聞かれているか判定し、**該当する reference を読んでから**回答する。複数該当する場合は全部読む。

| 話題 | 読むファイル |
|---|---|
| 太字・リンク・画像・表・折り畳み・脚注・エスケープなど基本構文 | `references/01-core-syntax.md` |
| ページ一覧、記事の検索・列挙、`%%変数%%`、URLでページを切り替える | `references/02-listpages.md` |
| `[[module ...]]` 全般、CSS モジュール、Rate、Comments、MailForm など | `references/03-modules.md` |
| `_template`、カテゴリ、`====`、404、DOM構造、CSSの当て方、データフォーム | `references/04-structure-and-templates.md` |
| SCP-JP / SCP-EN 固有（クレジット、image-block、jstyles、ルビ・圏点・縦書き、ACS、テーマ、CSSポリシー） | `references/05-scp-jp.md` |
| 「凝ったギミックを作りたい」「あの記事のアレはどうやっているのか」「バグ利用技」 | `references/06-hacks-and-bugs.md` |
| 「動かない」「壊れた」「なぜかこうなる」 | `references/07-pitfalls.md` |
| 一次情報の所在、他人の実装の読み方、ソースの一括取得 | `references/08-sources.md` |

## 回答時の原則

1. **構文は必ず reference から引く。** 特に `[[image]]` の属性、ListPages のセレクタ、`[[collapsible]]` のオプション、`[[#ifexpr]]` は記憶が当てにならない。
2. **行頭必須タグを守る。** `[[div]]` `[[/div]]` `[[collapsible]]` `[[code]]` `[[html]]` `[[=]]` などは単独行に置く。行末にスペースすら置かない。
3. **SCP-JP に投稿する記事なら、評価モジュールは `credit:start` / `credit:end` を使う。** 素の `[[module Rate]]` は現在ルール上使用禁止。
4. **「動かない」と言われたら `07-pitfalls.md` を先に見る。** 60項目の既知の癖がほぼ網羅されている。特に多いのは (a) `>` の後のスペース抜け、(b) タグが単独行になっていない、(c) `[[/div]]` の閉じ忘れ、(d) モジュール本文に `[[html]]`/`[[code]]` を入れている、(e) `====` の誤爆。
5. **ページが崩壊して編集できないと言われたら** `…/<page>/norender/true` を案内する。
6. **バグ利用技を提案するときは仕様外であることを明示する。** Wikidot 側の変更で壊れうる。またナビゲーション・評価モジュール・翻訳モジュールを壊す実装は SCP の CSS ポリシー違反になる。
7. **実装例が欲しいときは他人のページソースを読ませる。** ページ下部 Options → Page Source、または `…/printer--friendly//<page>`、`…/<page>/code/N`。プログラムから取るなら `scripts/fetch_wikidot_sources.py`（`ukwhatn/wikidot.py` 使用）。
8. **検証はサンドボックス（`scp-jp-sandbox3`）で。** 子ページに依存するギミックはサンドボックスで作れないので、単一ページ版（`06-hacks-and-bugs.md` A-4）にしておくと検証できる。

## よく使う雛形

SCP-JP の記事冒頭:
```
[[include :scp-jp:credit:start]]
**タイトル:** SCP-XXX-JP - タイトル
**著者:** [[*user あなたのアカウント名]]
**作成年:** 20XX
[[include :scp-jp:credit:end]]

[[include :scp-jp:component:image-block
name=画像URL|
caption=説明|
width=300px]]

**アイテム番号:** SCP-XXX-JP

**オブジェクトクラス:** Euclid

**特別収容プロトコル:** …

**説明:** …
```

日本語組版を使う場合はさらに:
```
[[include :scp-jp:component:jstyles]]
```
（導入すると `{{teletype}}` が等幅でなくなる点を必ず伝える）

## スクリプト

- `scripts/fetch_wikidot_sources.py` — Wikidot のページソースを一括取得する。`pip install wikidot` が必要。カテゴリ指定・サイト全体・除外接頭辞に対応。
