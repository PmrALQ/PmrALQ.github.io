# -*- coding: utf-8 -*-
"""Verify exact shapes of all 8 targets: full def, useI18n line, call site line."""
import os, re

ROOT = r"D:\self_website"
TARGETS = [
    "components/ArchiveTimeline.vue",
    "components/BlogCard.vue",
    "components/BlogList.vue",
    "components/ChangelogComponent.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

def brace_match(lines, start_idx):
    depth = 0
    started = False
    for i in range(start_idx, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if "{" in lines[i]:
            started = True
        if started and depth == 0:
            return i
    return None

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    print("#" * 74)
    print("FILE:", rel)
    if not os.path.exists(p):
        print("  !! MISSING")
        continue
    lines = open(p, encoding="utf-8").read().splitlines()
    print("total_lines:", len(lines))

    for i, ln in enumerate(lines):
        if "useI18n()" in ln:
            print("useI18n[%d]: %r" % (i + 1, ln))

    def_idxs = [i for i, ln in enumerate(lines) if re.search(r"\bfunction\s+formatDate\s*\(", ln)]
    print("def_lines:", [d + 1 for d in def_idxs])
    for di in def_idxs:
        end = brace_match(lines, di)
        if end is None:
            print("  !! cannot brace-match from line %d" % (di + 1))
            continue
        print("  -- def block (%d..%d):" % (di + 1, end + 1))
        for j in range(di, end + 1):
            print("    %4d| %r" % (j + 1, lines[j]))
    print()
