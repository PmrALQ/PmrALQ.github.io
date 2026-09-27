# -*- coding: utf-8 -*-
"""DRY-RUN: plan exact edits for formatDate extraction across 8 targets."""
import os, re

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

def find_func_block(lines, start_idx):
    """Return (def_line_idx, end_line_idx) of the function body via brace matching."""
    brace_open = None
    depth = 0
    for i in range(start_idx, len(lines)):
        if brace_open is None:
            if "{" in lines[i]:
                brace_open = i
                depth = lines[i].count("{") - lines[i].count("}")
        else:
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0:
                return (start_idx, i)
    return None

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    lines = open(p, encoding="utf-8").read().splitlines()
    print("=" * 72)
    print("FILE:", rel)
    print("=" * 72)

    # find function defs (may be multiple per file? expected 1)
    def_idxs = [i for i, ln in enumerate(lines) if re.search(r"function\s+formatDate\s*\(", ln)]
    for di in def_idxs:
        block = find_func_block(lines, di)
        if block:
            info = "\n".join("%4d| %s" % (j + 1, lines[j]) for j in range(block[0], block[1] + 1))
            print("-- function at line %d-%d:" % (block[0] + 1, block[1] + 1))
            print(info)
        else:
            print("-- [could not parse] line %d: %s" % (di + 1, lines[di]))

    # template call sites
    for i, ln in enumerate(lines):
        if "formatDate(" in ln and "function formatDate" not in ln:
            print("-- call site line %d: %s" % (i + 1, ln.strip()))

    # useI18n destructure line
    for i, ln in enumerate(lines):
        if "useI18n()" in ln:
            print("-- useI18n line %d: %s" % (i + 1, ln.strip()))
    print()
