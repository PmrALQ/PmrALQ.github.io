# -*- coding: utf-8 -*-
"""Health-check script: scan all 8 targets for ACTIVE formatDate defs, call sites,
and doubled comment markers. Pure read-only."""
import os
import re

ROOT = r"D:\self_website"

ALL_FILES = [
    "components/ArchiveTimeline.vue",
    "components/BlogList.vue",
    "components/BlogCard.vue",
    "components/ChangelogEntry.vue",
    "components/ProjectCall.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

for rel in ALL_FILES:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print("MISSING:", rel)
        continue
    lines = open(p, encoding="utf-8").read().splitlines()
    print("=" * 72)
    print("FILE:", rel)
    active_def_found = False
    for i, ln in enumerate(lines, 1):
        s = ln.rstrip()
        # active def?
        if re.search(r"^\s*function\s+formatDate\s*\(", s):
            print("  [ACTIVE DEF] line %d: %s" % (i, s))
            active_def_found = True
        # call site in template
        if "formatDate(" in s and "function formatDate" not in s:
            print("  [CALL] line %d: %s" % (i, s))
        # doubled comment markers
        if re.search(r"^\s*//\s*//\s*", s):
            print("  [DOUBLE-COMMENT] line %d: %s" % (i, s))
        # useI18n line
        if "useI18n()" in s:
            print("  [USEI18N] line %d: %s" % (i, s))
    if not active_def_found:
        print("  (no active formatDate def)")
