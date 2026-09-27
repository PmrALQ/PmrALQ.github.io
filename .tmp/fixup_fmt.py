# -*- coding: utf-8 -*-
"""Idempotent fixup: comment out any ACTIVE local formatDate defs, ensure call sites
carry the right options, and clean up doubled comment markers. Finally verify every
file that references formatDate has no active local def.
"""
import os
import re

ROOT = r"D:\self_website"

ALL_FILES = [
    "components/ArchiveTimeline.vue",
    "components/BlogList.vue",
    "components/BlogCard.vue",
    "components/ProjectCard.vue",
    "components/ChangelogEntry.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

# desired call-site forms per file; only these are "fixed"
CALL_OPTIONS = {
    "components/ArchiveTimeline.vue": ("{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}"),
    "components/ChangelogEntry.vue": ("{{ formatDate(entry.date) }}", "{{ formatDate(entry.date, { month: 'long' }) }}"),
    "pages/blog/[slug].vue": ("{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
    "pages/gallery/index.vue": ("{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}"),
    "pages/projects/[slug].vue": ("{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
}

FUNC_START_RE = re.compile(r"^(\s*)function\s+formatDate\s*\(dateStr\s*:\s*string\)\s*:\s*string\s*\{")
USEI18N_START_RE = re.compile(r"^(\s*)const\s*\{\s*([^}]*?)\s*\}\s*=\s*useI18n\(\)")


def read_lines(path):
    txt = open(path, "rb").read()
    try:
        txt = txt.decode("utf-8")
    except UnicodeDecodeError:
        txt = txt.decode("utf-8-sig")
    return txt.split("\n"), "\r\n" if "\r\n" in txt else "\n"


def brace_end(lines, start):
    depth = 0
    started = False
    for i in range(start, len(lines)):
        t = re.sub(r"'(?:[^'\\]|\\.)*'", "''", lines[i])
        t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)
        depth += t.count("{") - t.count("}")
        if "{" in t:
            started = True
        if started and depth == 0:
            return i
    return None


def is_comment_line(ln):
    return ln.strip().startswith("//") or ln.strip().startswith("*")


def comment_active_func(lines, di):
    """If the line at di is an ACTIVE (non-commented) function, wrap the whole block
    in a / *  * / comment with per-line prefixes."""
    if is_comment_line(lines[di]):
        return lines, 0
    ei = brace_end(lines, di)
    if ei is None:
        return lines, 0
    count = 0
    out = lines[:di]
    out.append("/*")
    out.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），此处保留原始实现仅供回溯。")
    for j in range(di, ei + 1):
        raw = lines[j]
        out.append(" *" + ((" " + raw) if raw.strip() else ""))
    out.append(" */")
    out.extend(lines[ei + 1 :])
    return out, 1


def clean_double_comment(lines):
    """Collapse lines like  // // const ... into a single // comment, and drop
    duplicated trailing note text."""
    out = []
    changed = 0
    for ln in lines:
        new = re.sub(r"^(\s*)//\s*//\s*", r"\1// ", ln)
        if new != ln:
            changed += 1
        out.append(new)
    return out, changed


def summary(rel, ops):
    print("[%s] %s" % (rel, " | ".join(ops) if ops else "no changes needed"))


def main():
    for rel in ALL_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("[SKIP %s] not found" % rel)
            continue
        lines, nl = read_lines(path)
        ops = []

        # 1) comment any active def
        for i, ln in enumerate(lines):
            if FUNC_START_RE.search(ln):
                before = "\n".join(lines)
                lines, n = comment_active_func(lines, i)
                if n:
                    ops.append("commented active def at line %d" % (i + 1))
                break

        # 2) idempotent call-site fix
        if rel in CALL_OPTIONS:
            old, new = CALL_OPTIONS[rel]
            blob = "\n".join(lines)
            cnt = blob.count(old)
            if cnt == 1:
                blob = blob.replace(old, new)
                lines = blob.split("\n")
                ops.append("call-site updated")
            elif cnt > 1:
                print("[WARN %s] call %r appears %d times, skipping" % (rel, old, cnt))

        # 3) clean doubled comment markers
        lines, ch = clean_double_comment(lines)
        if ch:
            ops.append("collapsed %d double-comment markers" % ch)

        # write
        out_text = "\n".join(lines).replace("\n", nl)
        if out_text != open(path, "rb").read().decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\n", "\r\n") if False else True:
            pass
        open(path, "wb").write(out_text.encode("utf-8"))
        summary(rel, ops)

    # 3) global verification
    print("-" * 60)
    print("VERIFY: search for active local formatDate defs outside utils/date.ts")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = {d for d in dirnames if d not in {"node_modules", ".git", ".nuxt", ".output", "dist", ".data", ".cache"}}
        for fn in filenames:
            if fn.endswith((".vue", ".ts", ".js", ".mjs", ".tsx")):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, ROOT).replace("\\", "/")
                if rel == "utils/date.ts":
                    continue
                try:
                    txt = open(p, encoding="utf-8").read()
                except Exception:
                    continue
                for i, ln in enumerate(txt.split("\n"), 1):
                    if FUNC_START_RE.search(ln) and not is_comment_line(ln.lstrip()):
                        print("  !! ACTIVE def in %s:%d: %s" % (rel, i, ln.strip()))
    print("VERIFY done")


if __name__ == "__main__":
    main()
