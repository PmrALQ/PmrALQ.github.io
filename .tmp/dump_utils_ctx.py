# -*- coding: utf-8 -*-
"""Dump utils/tags.ts content + full script blocks of formatDate targets."""
import os

ROOT = r"D:\self_website"

print("=" * 70)
print("FILE: utils/tags.ts")
print("=" * 70)
try:
    print(open(os.path.join(ROOT, "utils", "tags.ts"), encoding="utf-8").read())
except Exception as e:
    print("[ERROR]", e)

TARGETS = [
    "components/ArchiveTimeline.vue",
    "components/BlogCard.vue",
    "components/BlogList.vue",
    "components/ChangelogEntry.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    lines = open(p, encoding="utf-8").read().splitlines()
    script_start = None
    for i, ln in enumerate(lines):
        if "<script" in ln:
            script_start = i
            break
    script_end = None
    if script_start is not None:
        for i in range(script_start + 1, len(lines)):
            if "</script" in lines[i]:
                script_end = i
                break
    print("=" * 70)
    print("FILE: %s  (script %s-%s)" % (rel, script_start + 1, script_end if script_end else "?"))
    print("=" * 70)
    if script_start is not None and script_end is not None:
        for j in range(script_start, min(script_end + 1, script_start + 60)):
            print("%4d| %s" % (j + 1, lines[j]))
        if script_end - script_start > 60:
            print("  ... (script truncated, %d lines total)" % (script_end - script_start + 1))
    print()
