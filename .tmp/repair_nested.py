# -*- coding: utf-8 -*-
"""Repair nested /* */ comment blocks caused by re-running the extraction.
For each file: scan lines; if a line is exactly '/*' (after strip) and we are
already inside a block comment, treat it as a nested marker: remove it, and
remove the *matching* ' */' line that closes it (the first following line that
is exactly ' */'). Also remove extra leading ' * ' prefixes produced by nesting.
"""
import os
import re

ROOT = r"D:\self_website"

FILES = [
    "components/ArchiveTimeline.vue",
    "components/BlogList.vue",
    "components/BlogCard.vue",
    "components/ProjectCard.vue",
    "components/ChangelogEntry.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

for rel in FILES:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        continue
    lines = open(path, encoding="utf-8").read().split("\n")
    new = []
    in_block = False
    removed = 0
    for ln in lines:
        s = ln.strip()
        if s == "/*" and in_block:
            # nested opener: skip this line
            removed += 1
            continue
        if s == "*/" and in_block:
            in_block = False
            removed += 1
            continue
        if s == "/*" and not in_block:
            in_block = True
            new.append(ln)
            continue
        new.append(ln)
    txt = "\n".join(new)
    if "\n".join(lines) != txt:
        with open(path, "wb") as f:
            f.write(txt.encode("utf-8"))
        print("[FIXED] %s  removed=%d" % (rel, removed))
    else:
        print("[OK]   %s  no nested block" % rel)
