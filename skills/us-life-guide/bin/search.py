#!/usr/bin/env python3
"""在《高性价比人生指南·德州版 / 阿拉斯加版》中按关键词检索条目。

用法：
    python3 search.py texas 被裁 失业金
    python3 search.py alaska 熊 极寒 --top 8
    python3 search.py all 租房 押金 --top 5

输出每个命中条目的：文档、节、条目编号、标题、全文（含成本/说人话/收益/证据等级/来源）。
"""
import re
import sys
import os

DOCS = {
    "texas": os.path.expanduser("~/workspace/your_files/HowToLiveBetter-Texas.md"),
    "alaska": os.path.expanduser("~/workspace/your_files/HowToLiveBetter-Alaska.md"),
}

ENTRY_RE = re.compile(r"^###\s+(\d+)\.\s*(.*)$")
SECTION_RE = re.compile(r"^##\s+(.*?)\s*$")


def parse(path):
    """返回 [(section, number, title, full_text)]"""
    entries = []
    section = ""
    cur = None  # [number, title, lines]
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = SECTION_RE.match(line.rstrip("\n"))
            if m and not line.startswith("###"):
                section = m.group(1).strip()
                continue
            m = ENTRY_RE.match(line.rstrip("\n"))
            if m:
                if cur:
                    entries.append((section, cur[0], cur[1], "".join(cur[2]).strip()))
                cur = [m.group(1), m.group(2).strip(), [line]]
            elif cur:
                if line.startswith("## ") and not line.startswith("###"):
                    # 新的节开始：先收尾当前条目
                    entries.append((section, cur[0], cur[1], "".join(cur[2]).strip()))
                    cur = None
                    section = SECTION_RE.match(line.rstrip("\n")).group(1).strip()
                else:
                    cur[2].append(line)
    if cur:
        entries.append((section, cur[0], cur[1], "".join(cur[2]).strip()))
    return entries


def score(entry, keywords):
    section, number, title, text = entry
    blob = (title + "\n" + text).lower()
    s = 0
    for kw in keywords:
        k = kw.lower()
        cnt = blob.count(k)
        if cnt == 0:
            return -1  # 所有关键词至少出现一次（AND 语义）
        # 标题命中权重更高
        s += cnt + (3 if k in title.lower() else 0)
    return s


def main():
    args = sys.argv[1:]
    top = 5
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    which, keywords = args[0], args[1:]
    docs = DOCS if which == "all" else {which: DOCS[which]}

    hits = []
    for name, path in docs.items():
        for entry in parse(path):
            sc = score(entry, keywords)
            if sc > 0:
                hits.append((sc, name, entry))
    hits.sort(key=lambda h: -h[0])
    hits = hits[:top]

    if not hits:
        print("没有命中条目。换关键词再试（比如更短、更口语的词）。")
        return
    for sc, name, (section, number, title, text) in hits:
        print(f"===== [{name}] 第{section} · 第 {number} 条 =====")
        print(text)
        print()


if __name__ == "__main__":
    main()
