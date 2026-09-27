# -*- coding: utf-8 -*-
"""FINAL analysis: exact def bodies, call sites, t/locale usage per file."""
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

def extract_braces(lines, start_idx):
    depth = 0
    started = False
    for i in range(start_idx, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return i
    return None

out = []
for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    lines = open(p, encoding="utf-8").read().splitlines()
    out.append("=" * 72)
    out.append("FILE: %s" % rel)
    out.append("=" * 72)

    for i, ln in enumerate(lines):
        if re.search(r"\bfunction\s+formatDate\s*\(", ln):
            end = extract_braces(lines, i)
            out.append("-- DEF body (lines %d-%d):" % (i + 1, end + 1))
            out.extend(lines[i : end + 1])
            out.append("-- END DEF")

    for i, ln in enumerate(lines):
        if "formatDate(" in ln and "function formatDate" not in ln:
            out.append("-- CALL line %d: |%s|" % (i + 1, ln.rstrip()))

    out.append("-- t/locale refs:")
    tmpl_lines = [ln for ln in lines if re.search(r"\bt\(", ln) or re.search(r"\blocale\b", ln)]
    for ln in tmpl_lines:
        out.append("   | %s" % ln.rstrip())
    out.append("")
    out.append("")

text = "\n".join(out)
with open(os.path.join(ROOT, ".tmp", "final_analysis.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print("written final_analysis.txt lines=%d" % len(out))
