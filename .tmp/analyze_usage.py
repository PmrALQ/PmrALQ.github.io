# -*- coding: utf-8 -*-
"""Detailed per-file analysis: useI18n destructure & locale/t usage counters."""
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

for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    txt = open(p, encoding="utf-8").read()
    lines = txt.splitlines()
    print("=" * 70)
    print("FILE:", rel)
    print("=" * 70)

    for i, ln in enumerate(lines):
        if "useI18n" in ln:
            print("  useI18n@%d: %s" % (i + 1, ln.strip()))

    def_start = None
    brace_open = None
    depth = 0
    def_end = None
    for i, ln in enumerate(lines):
        if "function formatDate" in ln:
            def_start = i
        if def_start is not None and brace_open is None:
            if "{" in ln:
                brace_open = i
                depth = ln.count("{") - ln.count("}")
        elif brace_open is not None:
            depth += ln.count("{") - ln.count("}")
            if depth <= 0:
                def_end = i
                print("  formatDate def: lines %d-%d" % (def_start + 1, i + 1))
                break

    body_lines = []
    for i, ln in enumerate(lines):
        if def_start is None or i < def_start or i > (def_end or def_start):
            body_lines.append(ln)
    t_uses = sum(len(re.findall(r"\bt\(", ln)) for ln in body_lines)
    locale_uses = sum(len(re.findall(r"\blocale\b", ln)) for ln in body_lines)
    print("  't(' total usages (outside def):", t_uses)
    print("  'locale' total refs (outside def):", locale_uses)
    print()
