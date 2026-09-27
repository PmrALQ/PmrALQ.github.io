# -*- coding: utf-8 -*-
"""formatDate extraction controller. Modes: --plan | --apply
--plan: print every intended edit, write nothing.
--apply: perform edits with per-file assertions; abort file on any mismatch.
"""
import os
import re
import sys

ROOT = r"D:\self_website"

ALL_FILES = [
    "components/ArchiveTimeline.vue",
    "components/BlogList.vue",
    "components/ChangelogEntry.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

# Files whose template call site must carry explicit options:  (file, old, new)
CALL_SITE_EDITS = [
    ("components/ArchiveTimeline.vue", "{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}"),
    ("components/ChangelogEntry.vue", "{{ formatDate(entry.date) }}", "{{ formatDate(entry.date, { month: 'long' }) }}"),
    ("pages/blog/[slug].vue", "{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
    ("pages/gallery/index.vue", "{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}"),
    ("pages/projects/[slug].vue", "{{ formatDate(page?.date) }}", "{{ formatDate(page?.date, { month: 'long' }) }}"),
]

# Files to adjust useI18n destructure when variables become unused after def removal
#  (file, old_line_fragment, new_line_fragment)
USEI18N_EDITS = [
    ("components/ArchiveTimeline.vue", "const { t, locale } = useI18n()", "const { t } = useI18n()"),
    ("components/BlogList.vue", "const { t, locale } = useI18n()", "const { t } = useI18n()"),
]

ALL_PATH = list(ALL_FILES)


def read_lines(path):
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8-sig")
    return text, "\r\n" if "\r\n" in text else "\n"


def find_def_end(lines, di):
    depth = 0
    started = False
    for i in range(di, len(lines)):
        t = re.sub(r"'(?:[^'\\]|\\.)*'", "''", lines[i])
        t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', t)
        depth += t.count("{") - t.count("}")
        if "{" in t:
            started = True
        if started and depth == 0:
            return i
    return None


def plan_file(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        print("[SKIP %s] not found" % rel)
        return None
    text, nl = read_lines(path)
    lines = text.replace("\r\n", "\n").split("\n")

    def_idxs = [i for i, l in enumerate(lines) if "function formatDate" in l]
    if len(def_idxs) != 1:
        print("[FAIL %s] def count=%d" % (rel, len(def_idxs)))
        return None
    di = def_idxs[0]
    ei = find_def_end(lines, di)
    if ei is None:
        print("[FAIL %s] brace match failed" % rel)
        return None

    block = lines[di : ei + 1]
    ops = [("COMMENT", "%d-%d" % (di + 1, ei + 1), "\n".join(block))]

    for f, old, new in [e for e in CALL_SITE_EDITS if e[0] == rel]:
        c = text.count(old)
        if c != 1:
            print("[FAIL %s] call-site %r count=%d" % (rel, old, c))
            return None
        ops.append(("CALL", "tmpl", "%r -> %r" % (old, new)))

    for f, old, new in [e for e in USEI18N_EDITS if e[0] == rel]:
        c = text.count(old)
        if c != 1:
            print("[FAIL %s] useI18n %r count=%d" % (rel, old, c))
            return None
        ops.append(("USEI18N", "script", "%r -> %r" % (old, new)))

    print("=" * 72)
    print("[PLAN] %s" % rel)
    for kind, loc, detail in ops:
        print("  %-8s @%-7s %s" % (kind, loc, detail.replace("\n", " | ")[:160]))
    return rel


def apply_file(rel):
    path = os.path.join(ROOT, rel)
    text, nl = read_lines(path)
    lines = text.replace("\r\n", "\n").split("\n")

    def_idxs = [i for i, l in enumerate(lines) if "function formatDate" in l]
    if len(def_idxs) != 1:
        print("[FAIL %s] def count=%d" % (rel, len(def_idxs)))
        return False
    di = def_idxs[0]
    ei = find_def_end(lines, di)
    if ei is None:
        print("[FAIL %s] brace match failed" % rel)
        return False

    block = lines[di : ei + 1]
    commented = ["/*"]
    commented.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），")
    commented.append(" * 此处保留原始实现供回溯。")
    for l in block:
        commented.append(" *" + ((" " + l) if l.strip() else ""))
    commented.append(" */")

    out = lines[:di] + commented + lines[ei + 1 :]
    out_text = "\n".join(out)

    for old, new in [e for e in CALL_SITE_EDITS if e[0] == rel]:
        if out_text.count(old) != 1:
            print("[FAIL %s] call-site %r count!=1" % (rel, old))
            return False
        out_text = out_text.replace(old, new, 1)

    for old, new in [e for e in USEI18N_EDITS if e[0] == rel]:
        if out_text.count(old) != 1:
            print("[FAIL %s] useI18n %r count!=1" % (rel, old))
            return False
        out_text = out_text.replace(old, new, 1)

    with open(path, "wb") as fh:
        fh.write(out_text.replace("\n", nl).encode("utf-8"))
    print("[WROTE] %s" % rel)
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    ok = 0
    for rel in ALL_PATH:
        if mode == "apply":
            if apply_file(rel):
                ok += 1
        else:
            if plan_file(rel):
                ok += 1
    print("-" * 60)
    print("mode=%s processed=%d/%d" % (mode, ok, len(ALL_PATH)))


if __name__ == "__main__":
    main()
