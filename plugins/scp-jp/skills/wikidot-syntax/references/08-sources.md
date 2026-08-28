# 08 — 一次情報の所在と調査手法

## 1. 情報源マップ

### Wikidot 公式（唯一の仕様書。古く不完全だが一次情報）
| ページ | 内容 |
|---|---|
| `www.wikidot.com/doc-wiki-syntax:start` | 構文トップ。配下38ページが全構文 |
| `doc:quick-reference` / `doc:quick-reference-mini` | 早見表 |
| `doc-modules:start` | モジュール一覧。配下49ページ |
| `doc:expressions` | `[[#if]]` `[[#ifexpr]]` `[[#expr]]`（ここにしか載っていない） |
| `doc:templates` | `_template`、`====` 分割、`_404`、変数一覧 |
| `doc:site-structure` | サイト/ページ/カテゴリ/タグ/親/フォーラムの構造 |
| `doc:layout-reference` | ページDOM構造とPro向けカスタムレイアウト |
| `doc-data-forms:start` | データフォーム（29ページ） |
| `doc:searching` | 検索クエリ構文 |
| `doc:thumbnails` / `doc:api` | サムネイルURL / XML-RPC API |
| `doc-include:page-selection` | ListPages/CountPages 共通のセレクタ定義（実体はここ） |
| `snippets.wikidot.com` | コードスニペット集（`code:html5player` 等） |
| `community.wikidot.com` | howto 群 |

### SCP-JP
| ページ | 内容 |
|---|---|
| `wiki-syntax:startpage` ＋配下39ページ | 公式docの和訳＋加筆。実質日本語版仕様書 |
| `wiki-syntax` | 執筆でよく使う構文の要約 |
| `how-to-write:format` | 実務で必要な最小セット。クレジット必須化の告知もここ |
| `japanese-syntax` | jstyles（日本語組版） |
| `esoteric-syntax` | 難解Wikidot構文（HTMLブロック拡張、ページ改変、疑似フォーラム、Colmod 等） |
| `how-to-wikidot` | Wikidot そのものの使い方。壊れたページの救出手順 |
| `custom-theme-policy` / `custom-theme-jp` / `css-previewer` / `css-theme-preparation-tool` | テーマ関連 |
| `anomaly-classification-system-guide` | ACS |
| `storage-guide` / `licensing-guide` / `image-use-policy` | ファイル・ライセンス |
| `component:*` / `theme:*` | コンポーネント実装本体（ソースを読むのが最速） |

### SCP-EN
| ページ | 内容 |
|---|---|
| `wiki-syntax` | SCP-JP 版からの逆輸入＋EN固有 |
| `advanced-formatting-and-you`（DrMagnus） | div/CSS/iframe/ListPages の実践入門 |
| `scp-style-resource`（S D Locke） | フォーマットのコピペ集 |
| `css-policy` | CSS テーマの規約 |
| `theme:black-highlighter-theme` / `black-highlighter-themes` | 現行の主要テーマ |
| `components-hub` | コンポーネント一覧 |

### C-take 実験室（`shitake-crude-production.wikidot.com`）
非公式だが、Wikidot の挙動を実験で検証した記録として最も価値が高い。**実測 962 ページ**（著者分布: C-take 518 / Dr Devan 151 / physicslike 78 / 7happy7 76 / Nanimono Demonai 71 / shu_yabiyabi 25 ほか）。

| ページ/カテゴリ | 種別 | 内容 |
|---|---|---|
| `syntax-group`（皆の構文広場） | **親ページ**（category=0, page-itself=1。実測で `parent="syntax-group"` の子24件） | 遠隔折り畳み、閲覧者アイコン、rate数による表示、パスワード分岐、脚注/表/タイトル/折り畳みの強化 等 |
| `random-tech-group`（ランダム技術） | **親ページ**（子4件が `parent="random-tech-group"`） | ノイズCSS、時限式移動、奇声言語 |
| `basestudy:*`（基礎研究室） | カテゴリ | postMessage の挙動、コードブロックとページ遷移の不具合調査 |
| `module-specification` | **親ページ** | モジュール仕様書の総論 |
| `specification:*` | カテゴリ（3ページ） | モジュール仕様の個別研究（`specification:listpagesmodule-study` が特に重要） |
| `whatinclude` / `whathubinclude` | 個別ページ | インクルードと深層インクルードの原理 |
| `extension:*` / `javascript:*` / `csslab:*` / `snippet:*` | カテゴリ | 実装本体 |
| `component:*` / `theme:*` | カテゴリ | 各種テーマの原本 |

---

## 2. 調査手法

### ページソースを読む
1. ページ下部の **Options → Page Source**。他人の実装を全部読める。DrMagnus のエッセイでも最初に紹介されている
2. `…/printer--friendly//<page>` … サイドバー等を剥いだ本文（HTML取得が軽い）
3. `…/<page>/norender/true` … レンダリングせずに開く
4. `…/<page>/code/N` / `…/<page>/code_/N` / `<site>.wdfiles.com/local--code/<enc>/N` … コードブロックの生データ

### `ukwhatn/wikidot.py` による一括取得（推奨）
```bash
pip install wikidot
```
```python
import wikidot
with wikidot.Client() as c:
    site = c.site.get("scp-jp")
    # カテゴリ内の全ページ名を列挙
    names = [p.fullname for p in site.pages.search(category="wiki-syntax", limit=500, perPage=250)]
    # 1ページのソース
    print(site.page.get("esoteric-syntax").source.wiki_text)
```
一括取得は `PageCollection.get_page_sources()` を使う（1リクエストで複数ページ分のソースが返る）。
`scripts/fetch_wikidot_sources.py` に実装済み。

`site.pages.search()` は ListPages と同じセレクタ（`category` `tags` `parent` `created_by` `rating` `order` `offset` `limit` `perPage` `range` `name` `fullname` `link_to` `created_at` `updated_at` `votes` `pagetype` `separate` `wrapper`）を受け付ける。

**注意**: `viewsource` は権限によって拒否される場合がある（`Your account has no permission to perform this action: moduleName: viewsource/ViewSourceModule`）。バッチ処理ではその分だけリトライするか読み飛ばす。

### その他
- `scpper.com` … SCP 各支部の統計DB
- サンドボックス `scp-jp-sandbox3.wikidot.com` … ギミックの検証場所
- `system:recent-changes` / `system:list-all-pages` / `system:page-tags`

---

## 3. 本リファレンス作成時のコーパス

| 収集元 | 取得ページ数 | ライセンス |
|---|---|---|
| `www.wikidot.com`（`doc-wiki-syntax` 38 / `doc-modules` 49 / `doc` 67 / `doc-data-forms` 29 / `faq` 8 / `doc-include` 3） | 195 | Copyright © All Rights Reserved, Wikidot Inc.（フッター確認済み） |
| `shitake-crude-production`（著者ページ・下書き等を除く技術系全部） | 650 | CC BY-SA 3.0（フッター確認済み） |
| `scp-jp`（`wiki-syntax:*` 全39 ＋ 主要ガイド・コンポーネント） | 65 | CC BY-SA 3.0（フッター確認済み） |
| `scp-wiki`（構文・CSS・テーマ・ACS 関連） | 17 | CC BY-SA 3.0（フッター確認済み） |
| 合計 | 927 | — |

本リファレンス作成時に確認したリビジョンは `esoteric-syntax` が rev.49（2025-07-05 更新）、`japanese-syntax` が rev.53（2024-07-14 更新）、`how-to-write:format` が rev.13（2024-03-12 更新）。**最新状態との差分は `scripts/fetch_wikidot_sources.py` で再取得して確認すること**（取得手順は本章「2. 調査手法」参照）。

---

## 4. 情報の鮮度に関する注意

- `esoteric-syntax` は 2017〜2018年由来の記述が多い。HTMLブロック拡張スクリプトは**本文の脚注で明示的にレガシー扱い**されている。「動画っぽい動画じゃない何か」の章はサンプルの html ファイルが機能不全で差し止め中。
- EN の基準テーマは **Sigma-10**（旧 Sigma-9）。Black Highlighter が主要な代替テーマ。
- Flash 依存の記述（`[[embedaudio]]` 公式サンプル、`component:audio-player` の autoplay）はすべて死んでいる。
- 新規実装なら、素の `[[iframe]]` ＋ 添付ファイル ＋ `postMessage` ＋ `[[module CSS]]` の組み合わせが最も寿命が長い。
