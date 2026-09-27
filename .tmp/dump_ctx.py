# -*- coding: utf-8 -*-
"""Print import section + formatDate context for each file (read-only)."""
import os

ROOT = r"D:\self_website"
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
    print("=" * 70)
    print("FILE:", rel)
    print("=" * 70)
    if not os.path.exists(p):
        print("[MISSING]")
        continue
    lines = open(p, encoding="utf-8").read().splitlines()
    start = None
    for i, ln in enumerate(lines):
        if "<script" in ln:
            start = i
            break
    if start is not None:
        end = min(len(lines), start + 55)
        for i in range(start, min(len(lines), start + 80)):
            if "formatDate" in lines[i] and "function" in lines[i]:
                end = i + 1
                break
        print("--- script section (lines %d-%d):" % (start + 1, end))
        for j in range(start, end):
            print("%4d| %s" % (j + 1, lines[j]))
    print()
