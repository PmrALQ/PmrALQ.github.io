# -*- coding: utf-8 -*-
"""Scan all formatDate definitions & call sites (read-only, no modification)."""
import os, re, json

ROOT = r"D:\self_website"
SKIP_DIRS = {"node_modules", ".git", ".nuxt", ".output", "dist", ".data", ".claude", ".workbuddy"}
EXTS = {".vue", ".ts", ".js", ".mjs"}

results = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if not fn.endswith(tuple(EXTS)):
            continue
        p = os.path.join(dirpath, fn)
        try:
            lines = open(p, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        for i, ln in enumerate(lines, 1):
            if "formatDate" in ln:
                results.setdefault(rel, []).append(f"{i}:{ln.rstrip()}")

out = []
for rel in sorted(results):
    out.append(f"=== {rel} ===")
    for it in results[rel]:
        out.append(it)
    out.append("")

text = "\n".join(out)
with open(os.path.join(ROOT, ".tmp", "formatdate_scan.txt"), "w", encoding="utf-8") as f:
    f.write(text)
print(f"files_with_hits={len(results)} total_lines={sum(len(v) for v in results.values())}")
print("written:", os.path.join(ROOT, ".tmp", "formatdate_scan.txt"))
