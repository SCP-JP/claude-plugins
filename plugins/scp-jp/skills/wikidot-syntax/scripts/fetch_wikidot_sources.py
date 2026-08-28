#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["wikidot==4.5.2"]
# ///
"""
Wikidot のページソースを一括取得する。

uv があれば依存の導入は不要:
    uv run fetch_wikidot_sources.py scp-jp --category wiki-syntax -o out/

使い方:
    # カテゴリ配下を全部取る
    uv run fetch_wikidot_sources.py scp-jp --category wiki-syntax -o out/

    # 親ページの子を全部取る（「皆の構文広場」等はカテゴリではなく親ページ）
    uv run fetch_wikidot_sources.py shitake-crude-production --parent syntax-group -o out/

    # ページ名を明示指定
    uv run fetch_wikidot_sources.py scp-jp -p esoteric-syntax japanese-syntax -o out/

    # サイト全体（著者ページ等を除外）
    uv run fetch_wikidot_sources.py shitake-crude-production --all \
        --exclude author: draft: -o out/

出力:
    out/<site>/<fullname を __ 区切りにしたファイル名>.txt
    out/<site>/_index.json   （fullname / title / 文字数）

取得は fail-closed。1 ページでも取れなければ未取得一覧を出して終了コード 1 を返し、
既存の出力ディレクトリは書き換えない（新旧のソースが混ざったコーパスを作らないため）。
"""

import argparse
import json
import os
import shutil
import sys
import tempfile

import wikidot

BATCH = 40


def safe_name(fullname: str) -> str:
    return fullname.replace(":", "__").replace("/", "_")


def enumerate_pages(site, category="*", parent=None, limit=3000):
    """ListPages と同じセレクタでページ名を列挙する。"""
    kwargs = {"category": category, "limit": limit, "perPage": 250, "order": "fullname"}
    if parent:
        kwargs["parent"] = parent
    return [p.fullname for p in site.pages.search(**kwargs)]


def fetch_sources(site, names, outdir):
    """一時ディレクトリへ全件取得し、期待集合と一致したときだけ outdir を置き換える。"""
    staging = tempfile.mkdtemp(prefix="wikidot-fetch-")
    index = []
    acquired = set()
    try:
        for i in range(0, len(names), BATCH):
            chunk = names[i : i + BATCH]
            pages = [site.page.get(n, raise_when_not_found=False) for n in chunk]
            col = wikidot.PageCollection(site, [p for p in pages if p])
            try:
                # 1リクエストで複数ページ分のソースをまとめて取得する
                col.get_page_sources()
            except Exception as e:  # 権限エラー等はバッチ単位で落ちる
                print(f"  [warn] batch {i}: {type(e).__name__}: {e}", file=sys.stderr)
            for p in col:
                try:
                    text = p.source.wiki_text
                except Exception as e:
                    print(
                        f"  [warn] {p.fullname}: {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                    continue
                path = os.path.join(staging, safe_name(p.fullname) + ".txt")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                index.append(
                    {"fullname": p.fullname, "title": p.title, "len": len(text)}
                )
                acquired.add(p.fullname)
            print(f"  {min(i + BATCH, len(names))}/{len(names)}", file=sys.stderr)

        missing = [n for n in names if n not in acquired]
        if missing:
            print(
                f"\nFAIL: {len(missing)}/{len(names)} ページを取得できなかった。"
                f"既存の出力は変更していない。",
                file=sys.stderr,
            )
            for n in missing:
                print(f"  - {n}", file=sys.stderr)
            sys.exit(1)

        with open(os.path.join(staging, "_index.json"), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=1)

        # 全件揃ったのでここで初めて出力先を差し替える
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.makedirs(os.path.dirname(outdir) or ".", exist_ok=True)
        shutil.move(staging, outdir)
        staging = None
    finally:
        if staging and os.path.exists(staging):
            shutil.rmtree(staging)
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", help="Wikidot サイトの unix 名 (例: scp-jp)")
    ap.add_argument("-p", "--pages", nargs="*", default=[], help="取得するページ名")
    ap.add_argument("--category", default=None, help="このカテゴリを全取得")
    ap.add_argument("--parent", default=None, help="この親ページの子を全取得")
    ap.add_argument("--all", action="store_true", help="全カテゴリを取得")
    ap.add_argument(
        "--exclude", nargs="*", default=[], help="この接頭辞で始まるページを除外"
    )
    ap.add_argument("-o", "--outdir", default="out")
    args = ap.parse_args()

    outdir = os.path.join(args.outdir, args.site)

    with wikidot.Client() as client:
        site = client.site.get(args.site)
        print(f"site: {site.title} (id={site.id})", file=sys.stderr)

        names = list(args.pages)
        if args.all:
            names += enumerate_pages(site, "*")
        elif args.parent:
            names += enumerate_pages(site, "*", parent=args.parent)
        elif args.category:
            names += enumerate_pages(site, args.category)

        if args.exclude:
            ex = tuple(args.exclude)
            names = [n for n in names if not n.startswith(ex)]

        names = list(dict.fromkeys(names))  # 重複排除・順序保持
        if not names:
            print("targets: 0 — 取得対象が無い", file=sys.stderr)
            sys.exit(1)
        print(f"targets: {len(names)}", file=sys.stderr)

        index = fetch_sources(site, names, outdir)

    print(f"done: {len(index)} pages -> {outdir}", file=sys.stderr)


if __name__ == "__main__":
    main()
