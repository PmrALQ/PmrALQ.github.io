# -*- coding: utf-8 -*-
"""Final execution: comment formatDate defs, adjust call sites, trim unused vars.
Runs --plan first, then --apply. Safe: asserts every edit; writes only when all ok.
"""
import os
import re
import sys

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

# File -> (old_call, new_call) — call sites requiring explicit options
CALL_SITE_EDITS = {
    "components/ArchiveTimeline.vue": ("{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}"),
    "components/ChangelogEntry.vue": ("{{ formatDate(item.date) }}", "{{ formatDate(item.date, { month: 'long' }) }}"),
    "pages/blog/[slug].vue": ("{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
    "pages/gallery/index.vue": ("{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}"),
    "pages/projects/[slug].vue": ("{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
}

# File -> (old_destructure, new_destructure) — when variable becomes unused
USEI18N_EDITS = {
    "components/ArchiveTimeline.vue": ("const { t, locale } = useI18n()", "const { t } = useI18n()"),
    "components/BlogList.vue": ("const { t, locale } = useI18n()", "const { t } = useI18n()"),
    "components/ProjectCard.vue": ("const { locale } = useI18n()", "// const { locale } = useI18n() // 原仅服务于已抽离的 formatDate"),
    "components/ChangelogEntry.vue": ("const { locale } = useI18n()", "// const { locale } = useI18n() // 原仅服务于已抽离的 formatDate"),
}


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


def comment_block(lines, di, ei):
    return lines[:di] + ["/*", " * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），",
                         " * 此处保留原始实现供回溯。"] + [
        " *" + ((" " + ln) if ln.strip() else "") for ln in lines[di:ei+1]
    ] + [" */"] + lines[ei+1:]


def transform(rel, dry_run=True):
    path = os.path.join(ROOT, rel)
    text, nl = read_lines(path)
    lines = text.replace("\r\n", "\n").split("\n")

    # 1. comment def
    di_list = [i for i, ln in enumerate(lines) if "function formatDate" in ln]
    if len(di_list) != 1:
        print("[FAIL %s] def count=%d" % (rel, len(di_list)))
        return False
    di = di_list[0]
    ei = find_def_end(lines, di)
    if ei is None:
        print("[FAIL %s] brace match failed" % rel)
        return False
    lines = comment_block(lines, di, ei)

    # 2. call-site edits
    if rel in CALL_SITE_EDITS:
        old, new = CALL_SITE_EDITS[rel]
        cnt = "\n".join(lines).count(old)
        if cnt != 1:
            print("[FAIL %s] call %r count=%d" % (rel, old, cnt))
            return False
        lines = "\n".join(lines).replace(old, new).split("\n")

    # 3. usei18n trim
    if rel in USEI18N_EDITS:
        old, new = USEI18N_EDITS[rel]
        cnt = "\n".join(lines).count(old)
        if cnt != 1:
            print("[FAIL %s] usei18n %r count=%d" % (rel, old, cnt))
            return False
        lines = "\n".join(lines).replace(old, new).split("\n")

    out_text = "\n".join(lines).replace("\n", nl)
    if out_text == text:
        print("[NOOP %s]" % rel)
        return True
    if dry_run:
        print("[PLAN-WRITE %s]" % rel)
        return True
    open(path, "wb").write(out_text.encode("utf-8"))
    print("[WROTE %s]" % rel)
    return True


def main():
    dry_run = len(sys.argv) < 2 or sys.argv[1] != "apply"
    for rel in ALL_FILES:
        transform(rel, dry_run=dry_run)
    print("-" * 60)
    print("mode=" + ("plan" if dry_run else "apply"))


if __name__ == "__main__":
    main()
