# -*- coding: utf-8 -*-
"""Extract full function bodies of formatDate from each hit (read-only)."""
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

def extract_func(lines, start_idx):
    brace_start = None
    for i in range(start_idx, len(lines)):
        if "{" in lines[i]:
            brace_start = i
            break
    if brace_start is None:
        return None
    depth = 0
    started = False
    for i in range(brace_start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return (brace_start, i)
    return None

out = []
for rel in TARGETS:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        out.append("=== %s === [MISSING]" % rel)
        out.append("")
        continue
    lines = open(p, encoding="utf-8").read().splitlines()
    out.append("=== %s ===" % rel)
    for i, ln in enumerate(lines):
        if "function formatDate" in ln:
            span = extract_func(lines, i)
            if span:
                s, e = span
                body = "\n".join("%d: %s" % (j + 1, lines[j]) for j in range(s, e + 1))
                out.append("-- def at line %d (body %d-%d):" % (i + 1, s + 1, e + 1))
                out.append(body)
            else:
                out.append("-- def at line %d: [could not extract] %s" % (i + 1, ln))
    out.append("")

text = "\n".join(out)
with open(os.path.join(ROOT, ".tmp", "formatdate_bodies.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print("written")
