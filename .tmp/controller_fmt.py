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
    "components/BlogCard.vue",
    "components/BlogList.vue",
    "components/ChangelogEntry.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

# Files whose template call site must carry explicit options
CALL_SITE_EDITS = [
    ("components/ArchiveTimeline.vue", "{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}"),
    ("components/ChangelogEntry.vue", "{{ formatDate(entry.date) }}", "{{ formatDate(entry.date, { month: 'long' }) }}"),
    ("pages/blog/[slug].vue", "{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
    ("pages/gallery/index.vue", "{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}"),
    ("pages/projects/[slug].vue", "{{ formatDate(page?.date) }}", "{{ formatDate(page?.date, { month: 'long' }) }}"),
]

# Files to adjust useI18n destructure (only vars that become unused)
USEI18N_EDITS = [
    ("components/ArchiveTimeline.vue", "const { t, locale } = useI18n()", "const { t } = useI18n()"),
    ("components/BlogList.vue", "const { t, locale } = useI18n()", "const { t } = useI18n()"),
    ("components/BlogCard.vue", "const { locale } = useI18n()", "const { locale } = useI18n()"),  # keep, still used
]

BLOCK_COMMENT_HDR = "/*\n * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），\n * 此处保留原始实现供对比回溯。\n */"


def find_def(lines, start):
    """brace-matching end index for the function def from line index start."""
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


def process(rel, apply_changes):
    path = os.path.join(ROOT, rel)
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    norm = text.replace("\r\n", "\n")
    lines = norm.split("\n")

    # locate def
    def_idxs = [i for i, l in enumerate(lines) if "function formatDate" in l]
    if len(def_idxs) != 1:
        print("[FAIL %s] def idx count = %d" % (rel, len(def_idxs)))
        return False
    di = def_idxs[0]
    if not lines[di].lstrip().startswith("function formatDate"):
        print("[FAIL %s] def line malformed: %r" % (rel, lines[di]))
        return False
    ei = find_def(lines, di)
    if ei is None:
        print("[FAIL %s] cannot brace-match def block" % rel)
        return False

    block = lines[di : ei + 1]
    if "locale.value" not in "\n".join(block):
        print("[FAIL %s] def block does not reference locale.value" % rel)
        return False

    plan = []
    plan.append(("COMMENT-OUT def block", rel, di + 1, ei + 1,
                 "blocks: " + " | ".join(l.strip() for l in block)))

    # call-site edits for this file
    cs_edits = [e for e in CALL_SITE_EDITS if e[0] == rel]
    for old, new in cs_edits:
        cnt = norm.count(old)
        if cnt != 1:
            print("[FAIL %s] call pattern %r count = %d" % (rel, old, cnt))
            return False
        plan.append(("CALL-SITE", rel, "<template>", 0, "%r -> %r" % (old, new)))

    # useI18n edits for this file
    ui_edits = [e for e in USEI18N_EDITS if e[0] == rel]
    for old, new in ui_edits:
        if old != new and norm.count(old) != 1:
            print("[FAIL %s] useI18n pattern %r count != 1" % (rel, old))
            return False
        if old != new:
            plan.append(("USEI18N", rel, "<script>", 0, "%r -> %r" % (old, new)))

    if not apply_changes:
        for kind, f, s, e, detail in plan:
            print("[PLAN %s] %s lines %s: %s" % (kind, f, s if s != "<template>" else "T", detail))
        return True

    # apply
    out = lines[:di] + BLOCK_COMMENT_HDR.split("\n") + lines[ei + 1 :]
    text2 = "\n".join(out)
    for old, new in cs_edits:
        text2 = text2.replace(old, new, 1)
    for old, new in ui_edits:
        if old != new:
            text2 = text2.replace(old, new, 1)
    with open(path, "wb") as f:
        f.write(text2.replace("\n", nl).encode("utf-8"))
    print("[OK   %s] written (%d blocks commented)" % (rel, len(block)))
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "plan"
    apply_changes = mode == "apply"
    ok = 0
    for rel in ALL_FILES:
        if os.path.exists(os.path.join(ROOT, rel)):
            if process(rel, apply_changes):
                ok += 1
    print("-" * 60)
    print("mode=%s processed=%d/%d" % (mode, ok, len(ALL_FILES)))


if __name__ == "__main__":
    main()
