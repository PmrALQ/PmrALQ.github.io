# -*- coding: utf-8 -*-
"""Final extraction script for formatDate -> utils/date.ts.
- Comments out local def blocks (preserving source, per user constraint)
- Updates required template call sites with per-file options
- Leaves useI18n destructure untouched (no compile risk in TS default config)
All replacements are asserted; any mismatch aborts without writing that file.
"""
import os
import re

ROOT = r"D:\self_website"
NEWLINE = None  # detected per file

# file -> list of (old, new) call-site replacements (only for files whose default differs)
CALL_EDITS = {
    "components/ArchiveDetail.vue": None,  # placeholder; real list below
}

# Real target config: files whose call site needs explicit options
CALL_SITE_EDITS = [
    # ("relative_path", "old substring", "new substring", expected_count)
    ("components/ArchiveTimeline.vue", "{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}", 1),
    ("components/ChangelogEntry.vue", "{{ formatDate(entry.date) }}", "{{ formatDate(entry.date, { month: 'long' }) }}", 1),
    ("pages/blog/[slug].vue", "{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}", 1),
    ("pages/gallery/index.vue", "{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}", 1),
    ("pages/projects/[slug].vue", "{{ formatDate(page?.date) }}", "{{ formatDate(page?.date, { month: 'long' }) }}", 1),
]

# Files with default-style formatDate (year + short month) - call sites stay the same
DEFAULT_FILES = [
    "components/BlogCard.vue",
    "components/BlogList.vue",
    "components/ProjectCard.vue",
]

# All 8 files (7 components + 3 pages = actually unique list assembled below)
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


def detect_newline(text):
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def find_func_block(lines, def_idx):
    """Return end index of the function body starting at def_idx (brace matched)."""
    depth = 0
    started = False
    for i in range(def_idx, len(lines)):
        line = lines[i]
        # strip obvious string content to be safe (function bodies are simple in this repo)
        stripped = re.sub(r"'(?:[^'\\]|\\.)*'", "''", line)
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)
        depth += stripped.count("{") - stripped.count("}")
        if "{" in stripped:
            started = True
        if started and depth == 0:
            return i
    raise ValueError("unbalanced braces from line %d" % (def_idx + 1))


def block_to_comment(block):
    out = ["/*"]
    out.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），")
    out.append(" * 此处保留原始实现供对比回溯。")
    for ln in block:
        out.append((" *" + ln) if ln.strip() else " *")
    out.append(" */")
    return out


def process_file(rel):
    path = os.path.join(ROOT, rel)
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8-sig")
    nl = detect_newline(text)
    lines = text.split("\n")
    # normalize: split leaves no \r if nl == "\n"; if "\r\n", lines contain trailing \r
    # We handle by working on normalized text
    norm = text.replace("\r\n", "\n")

    # 1. locate & comment out def
    nm_lines = norm.split("\n")
    def_idxs = [i for i, ln in enumerate(nm_lines) if re.search(r"\bfunction\s+formatDate\s*\(", ln)]
    if len(def_idxs) != 1:
        return "[FAIL %s] expected exactly 1 def, found %d" % (rel, len(def_idxs))
    di = def_idxs[0]
    ei = find_func_block(nm_lines, di)
    block = nm_lines[di : ei + 1]
    # sanity check on the block
    if "locale.value" not in "\n".join(block):
        return "[FAIL %s] def block does not contain locale.value usage" % rel

    comment = block_to_comment(block)
    new_lines = nm_lines[:di] + comment + nm_lines[ei + 1 :]
    norm = "\n".join(new_lines)

    # 2. call-site replacements
    for old, new, expected in CALL_SITE_EDITS:
        if old not in norm:
            continue  # not this file
        cnt = norm.count(old)
        if cnt != expected:
            return "[FAIL %s] expected %d occurrence(s) of %r, found %d" % (rel, expected, old, cnt)
        norm = norm.replace(old, new)

    # 3. write back with original EOL style
    output = norm.replace("\n", nl)
    # preserve final newline
    if not output.endswith("\n"):
        output += "\n"
    open(path, "wb").write(output.encode("utf-8"))
    return "[OK   %s] def commented, call sites updated (if any)" % rel


def main():
    # 0. Create utils/date.ts
    util_path = os.path.join(ROOT, "utils", "date.ts")
    util_dir = os.path.dirname(util_path)
    if not os.path.isdir(util_dir):
        os.makedirs(util_dir)
    util_src = '''/**
 * 统一日期格式化工具。
 *
 * 原为多个组件内重复定义的局部函数，集中抽离至此复用（Nuxt 自动导入）。
 * 行为与原实现完全一致：
 * - 跟随当前 i18n locale（zh → zh-CN，其余 → en-US）
 * - 通过 options 控制年份显示与「月」的格式（short / long）
 */

export interface FormatDateOptions {
  /** 是否显示年份，默认 true */
  year?: boolean
  /** 月份显示格式：'short' 缩写（如「2月」/「Feb」），'long' 完整（如「二月」/「February」） */
  month?: 'short' | 'long'
}

/**
 * 将日期字符串格式化为当前语言环境下的可读日期。
 *
 * @param dateStr - ISO 日期字符串或可被 Date 解析的字符串
 * @param options - 显示选项
 */
export function formatDate(dateStr: string, options: FormatDateOptions = {}): string {
  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) return dateStr

  const { year = true, month = 'short' } = options
  const formatOptions: Intl.DateTimeFormatOptions = { day: 'numeric', month }
  if (year) formatOptions.year = 'numeric'

  const { locale } = useI18n()
  return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', formatOptions)
}
'''
    with open(util_path, "wb") as f:
        f.write(util_src.encode("utf-8"))
    print("[CREATED] utils/date.ts")

    # 1. Process all 8 files
    results = []
    for rel in ALL_FILES:
        if os.path.exists(os.path.join(ROOT, rel)):
            results.append(process_file(rel))
        else:
            results.append("[SKIP %s] file not found" % rel)
    print("\n".join(results))

    # 2. Print summary
    ok = [r for r in results if r.startswith("[OK")]
    fail = [r for r in results if not r.startswith("[OK")]
    print("-" * 60)
    print("OK: %d  FAIL/SKIP: %d" % (len(ok), len(fail)))
    if fail:
        print("\n".join(fail))


if __name__ == "__main__":
    main()
