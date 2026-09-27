# -*- coding: utf-8 -*-
"""Extract formatDate to utils/date.ts: comment out local defs, fix call sites & useI18n.
Safe-by-construction: every replacement is asserted; on any mismatch the file is left untouched.
"""
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

CALL_EDITS = {
    "components/ArchiveTimeline.vue": ("{{ formatDate(item.date) }}", "{{ formatDate(item.date, { year: false }) }}"),
    "components/ChangelogEntry.vue": ("{{ formatDate(entry.date) }}", "{{ formatDate(entry.date, { month: 'long' }) }}"),
    "pages/blog/[slug].vue": ("{{ formatDate(page.date) }}", "{{ formatDate(page.date, { month: 'long' }) }}"),
    "pages/gallery/index.vue": ("{{ formatDate(photo.date) }}", "{{ formatDate(photo.date, { month: 'long' }) }}"),
    "pages/projects/[slug].vue": ("{{ formatDate(page?.date) }}", "{{ formatDate(page?.date, { month: 'long' }) }}"),
}

USEI18N_COMMENT = "// 原 useI18n 解构中的 locale 已随 formatDate 抽离至 utils/date.ts（内部自行获取）"

def find_def_block(lines, def_idx):
    """Brace-match the function body; return end index."""
    depth = 0
    started = False
    for i in range(def_idx, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if "{" in lines[i]:
            started = True
        if started and depth == 0:
            return i
    raise ValueError("unbalanced braces from def line %d" % (def_idx + 1))


def comment_lines(block):
    out = ["/*"]
    out.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入提供），")
    out.append(" * 此处保留原始实现供对比回溯。")
    for ln in block:
        out.append((" *" + ln) if ln.strip() else " *")
    out.append(" */")
    return out


def main():
    report = []
    for rel in TARGETS:
        path = os.path.join(ROOT, rel)
        lines = open(path, encoding="utf-8").read().split("\n")
        orig = "\n".join(lines)

        # 1. locate def
        def_idxs = [i for i, ln in enumerate(lines) if "function formatDate" in ln]
        if len(def_idxs) != 1:
            report.append("[SKIP %s] def not found or multiple defs: %s" % (rel, def_idxs))
            continue
        def_idx = def_idxs[0]
        if not lines[def_idx].strip().startswith("function formatDate"):
            report.append("[SKIP %s] def line unexpected: %r" % (rel, lines[def_idx]))
            continue
        end_idx = find_def_block(lines, def_idx)
        block = lines[def_idx : end_idx + 1]

        # sanity: the body should mention locale.value and formatDate name
        block_txt = "\n".join(block)
        if "locale.value" not in block_txt:
            report.append("[SKIP %s] def body does not use locale.value" % rel)
            continue

        # 2. replace body with comment
        lines[def_idx : end_idx + 1] = comment_lines(block)

        # 3. call-site edits
        if rel in CALL_EDITS:
            old, new = CALL_EDITS[rel]
            joined = "\n".join(lines)
            cnt = joined.count(old)
            if cnt != 1:
                report.append("[SKIP %s] call-site pattern not unique (%d): %r" % (rel, cnt, old))
                continue
            lines = (joined.replace(old, new)).split("\n")

        # 4. useI18n line handling
        for i, ln in enumerate(lines):
            if "useI18n()" in ln and "const" in ln and "{" in ln:
                vars_ = ln.strip()
                # extract destructured names
                import re as _re
                m = _re.search(r"\{([^}]*)\}", vars_)
                if not m:
                    report.append("[SKIP %s] cannot parse destructure: %r" % (rel, ln))
                    continue
                var_names = [v.strip() for v in m.group(1).split(",") if v.strip()]
                # count occurrences of each var outside this line
                body = "\n".join(lines[:i] + lines[i + 1:])
                keep = [v for v in var_names if _re.search(r"\b" + _re.escape(v) + r"\b", body)]
                if set(keep) == set(var_names):
                    report.append("[OK   %s] useI18n destructure untouched: %s" % (rel, var_names))
                else:
                    old_line = ln
                    new_line = "const { " + ", ".join(keep) + " } = useI18n()" if keep else ""
                    lines[i] = "// " + old_line + "  // " + USEI18N_COMMENT
                    if new_line:
                        lines.insert(i + 1, new_line)
                    report.append("[EDIT %s] useI18n %s -> %s" % (rel, var_names, keep or "none"))
                break

        new_text = "\n".join(lines)
        if new_text == orig:
            report.append("[NOOP %s] nothing changed" % rel)
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_text)
        report.append("[WROTE %s]" % rel)

    print("\n".join(report))
    print("DONE")


if __name__ == "__main__":
    main()
