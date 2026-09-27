# -*- coding: utf-8 -*-
"""Scan ALL formatDate call sites in templates + defs (read-only)."""
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

CALL_RE = re.compile(r"formatDate\s*\(")

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    print("=" * 70)
    print("FILE:", rel)
    print("=" * 70)
    if not os.path.exists(p):
        print("[MISSING]")
        continue
    lines = open(p, encoding="utf-8").read().splitlines()
    in_template = False
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if "<template" in stripped:
            in_template = True
        if "</template" in stripped:
            in_template = False
        for m in CALL_RE.finditer(ln):
            seg = ln[max(0, m.start() - 60): m.end() + 80].strip()
            where = "TEMPLATE" if in_template else "SCRIPT"
            print("  [%s] line %d: ...%s..." % (where, i + 1, seg))
    print()
