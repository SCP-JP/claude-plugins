# SCP-JP Claude Code Plugins

SCP-JP コミュニティ向けに [Claude Code](https://claude.com/product/claude-code) の plugin を配布する marketplace。

Wikidot（SCP財団が使っているホスティングサービス）は Markdown でも MediaWiki でもない独自構文で、モジュール・テンプレート・CSS が密結合しており、記憶で書くと確実に間違える。ここで配布する plugin は、Wikidot / SCP-JP の執筆時に該当する構文リファレンスを Claude Code が自動的に参照するようにする skill を収録している。

## Install

```
/plugin marketplace add SCP-JP/claude-plugins
/plugin install scp-jp@scp-jp-plugins
```

## 収録 plugin

### scp-jp

Wikidot / SCP-JP の執筆に使う skill 一式。

- **wikidot-syntax** — Wikidot の構文・モジュール・テンプレート・CSS、および SCP-JP / SCP-EN 固有の拡張構文とギミック実装の完全リファレンス。Wikidot 構文や SCP記事の執筆、ページのギミック実装について聞かれると自動的に発火する。以下の8本の reference で構成:
  - `01-core-syntax.md` — 太字・リンク・画像・表・折り畳み・脚注など基本構文
  - `02-listpages.md` — ページ一覧・検索・列挙、`%%変数%%`
  - `03-modules.md` — `[[module ...]]` 全般（CSS / Rate / Comments / MailForm 等）
  - `04-structure-and-templates.md` — `_template`、カテゴリ、DOM構造、データフォーム
  - `05-scp-jp.md` — SCP-JP / SCP-EN 固有（クレジット、jstyles、ACS、テーマ、CSSポリシー）
  - `06-hacks-and-bugs.md` — 仕様外の挙動を利用したギミック実装（後述）
  - `07-pitfalls.md` — 「動かない」「壊れた」の既知の原因60項目
  - `08-sources.md` — 一次情報の所在と調査手法

## 06-hacks-and-bugs（ギミック実装）について

`references/06-hacks-and-bugs.md` に掲載しているテクニックは、すべて Wikidot の**仕様外の挙動**（バグ利用・未文書化の副作用）に依存している。

- Wikidot 側の実装変更で予告なく壊れうる。記事に組み込む場合はそのリスクを踏まえること
- **ナビゲーション・評価モジュール（Rate）・翻訳モジュールを壊す実装は SCP の CSS ポリシー違反になる**。これらを隠蔽・破壊するギミックは投稿不可
- 検証は本番サイトではなく**サンドボックス（`scp-jp-sandbox3`）**で行うこと。子ページに依存するギミックはサンドボックス上では作れないため、可能なら単一ページで完結する構成にする

## references の更新手順

Wikidot 公式・SCP-JP・shitake-crude-production 側の記述が更新された場合、同梱の `scripts/fetch_wikidot_sources.py` で原典を再取得し、差分を確認する。

```bash
pip install wikidot
python plugins/scp-jp/skills/wikidot-syntax/scripts/fetch_wikidot_sources.py scp-jp --category wiki-syntax -o out/
```

取得したソースと `references/` の記述を突き合わせ、差分があれば reference を更新する。

## 出典・謝辞

references は以下のコーパス（計927ページ）を基に作成している。

| 収集元 | 内容 | ページ数 | ライセンス |
|---|---|---|---|
| `www.wikidot.com`（公式ドキュメント） | 構文・モジュール仕様 | 195 | All Rights Reserved（Wikidot, Inc.） |
| `shitake-crude-production.wikidot.com` | 非公式の実験・実装記録 | 650 | CC BY-SA 3.0 |
| `scp-jp.wikidot.com` | SCP-JP固有の構文・ガイド | 65 | CC BY-SA 3.0 |
| `scp-wiki.wikidot.com` | SCP-EN固有の構文・ガイド | 17 | CC BY-SA 3.0 |

公式ドキュメントは全権利留保だが、references はその文章を複製・翻訳したものではない。仕様の事実確認に用いたうえで、構文記号・属性名・許可値などの**事実**だけを抽出し独自に構成・記述し直している。

主要な技法の出典元として、`shitake-crude-production`（C-take 氏ほか）と `scp-jp:esoteric-syntax`（寄稿者13名）に謝辞を表する。第三者技法・素材への個別クレジットは [LICENSE](./LICENSE) を参照。

## ライセンス

ドキュメント（`SKILL.md` / `references/`）とコード（`scripts/` 等）でライセンスが異なる。適用範囲の対応表・第三者notice を含め詳細は [LICENSE](./LICENSE) を参照。

## SCP-JP スタッフ向け

スタッフ限定の内容を含む plugin は別の非公開 marketplace（`claude-plugins-staff`）で配布している。詳細はそちらの README を参照。
