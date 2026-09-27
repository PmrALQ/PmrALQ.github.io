# -*- coding: utf-8 -*-
"""Fix remaining issues:
1. ChangelogEntry.vue: comment out ACTIVE formatDate def, update call site, trim destructure
2. ProjectCard.vue: clean doubled comment marker on the useI18n line
Prints before/after for every change; asserts uniqueness of targets.
"""
import os
import re

# ---------------------------------------------------------------------------
# 1. ChangelogEntry.vue
# ---------------------------------------------------------------------------
PATH = r"D:\self_website\components\ChangelogEntry.vue"
txt = open(PATH, encoding="utf-8").read()
orig = txt

old_call = "{{ formatDate(entry.date) }}"
new_call = "{{ formatDate(entry.date, { month: 'long' }) }}"
assert txt.count(old_call) == 1, "call site %r count=%d" % (old_call, txt.count(old_call))
txt = txt.replace(old_call, new_call)
print("[OK] ChangelogEntry.vue call site updated")

lines = txt.split("\n")
# find ACTIVE def: a line matching ^function formatDate (no leading //
def_idx = None
for i, ln in enumerate(lines):
    if re.match(r"^\s*function\s+formatDate\s*\(", ln):
        def_idx = i
        break
assert def_idx is not None, "active formatDate def not found"

# brace match
depth = 0
started = False
end_idx = None
for i in range(def_idx, len(lines)):
    depth += len(re.findall(r"\{", lines[i])) - len(re.findall(r"\}", lines[i]))
    if "{" in lines[i]:
        started = True
    if started and depth == 0:
        end_idx = i
        break
assert end_idx is not None, "def block brace match failed"

block = lines[def_idx : end_idx + 1]
print("  def block lines %d-%d" % (def_idx + 1, end_idx + 1))
comment = ["/*"]
comment.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），此处保留原始实现仅供回溯。")
for ln in block:
    comment.append(" *" + ((" " + ln) if ln.strip() else ""))
comment.append(" */")
lines[def_idx : end_idx + 1] = comment
print("  [OK] def commented out")

txt = "\n".join(lines)

# trim useI18n destructure if locale is no longer used anywhere
usei18n_line_idx = None
for i, ln in enumerate(lines):
    if "useI18n()" in ln and "const" in ln:
        usei18n_line_idx = i
        break
if usei18n_line_idx is not None:
    line = lines[usei18n_line_idx]
    # count locale uses in the whole file excluding this line
    rest = "\n".join(lines[:usei18n_line_idx] + lines[usei18n_line_idx + 1:])
    locale_uses = len(re.findall(r"\blocale\b", rest))
    t_uses = len(re.findall(r"\bt\b", rest))
    print("  useI18n line %d: %s" % (usei18n_line_idx + 1, line.strip()))
    print("  locale uses outside def:", locale_uses, "| t uses outside def:", t_uses)
    if locale_uses == 0:
        if "t" in line and t_uses > 0:
            lines[usei18n_line_idx] = (
                "// " + line + "  // 原解构项 locale 仅服务于已抽离至 utils/date.ts 的 formatDate\n"
                + lines[usei18n_line_idx].replace("locale", "").replace("const { t }", "const { t }") + ""
            )
            print("  [OK] useI18n line trimmed to t-only")
        else:
            lines[usei18n_line_idx] = "// " + line + "  // 原解构项仅服务于已抽离的 formatDate"
            print("  [OK] useI18n line fully commented")
    else:
        print("  [OK] destructure kept (locale still used)")

txt = "\n".join(lines)

with open(PATH, "wb") as f:
    f.write(txt.encode("utf-8"))
print("  [WROTE] ChangelogEntry.vue")

# ---------------------------------------------------------------------------
# 2. ProjectCard.vue — clean doubled comment markers
# ---------------------------------------------------------------------------
PATH2 = r"D:\self_website\components\ProjectCard.vue"
txt2 = open(PATH2, encoding="utf-8").read()
orig2 = txt2

# collapse patterns like "// // const ... // 原... // 原..." into a single
# clean comment line
pat = re.compile(r"^(\s*)//\s*//\s*", re.MULTILINE)
new_txt2 = pat.sub(r"\1// ", txt2)
# also collapse repeated trailing notes: " // 原仅服务于已抽离的 formatDate // 原仅服务于已抽离的 formatDate"
new_txt2 = re.sub(r"(// 原仅服务于已抽离的 formatDate)(\s*// 原仅服务于已抽离的 formatDate)+", r"\1", new_txt2)

if new_txt2 != txt2:
    with open(PATH2, "wb") as f:
        f.write(new_txt2.encode("utf-8"))
    print("[WROTE] ProjectCard.vue (cleaned double comments)")
else:
    print("[OK] ProjectCard.vue already clean")

# ---------------------------------------------------------------------------
# 3. Verify all: no ACTIVE formatDate def, expected call sites
# ---------------------------------------------------------------------------
print("-" * 60)
for rel in [
    "components/ArchiveTimeline.vue",
    "components/BlogList.vue",
    "components/BlogCard.vue",
    "components/ProjectCard.vue",
    "components/ChangelogEntry.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]:
    p = os.path.join(r"D:\self_website", rel)
    t = open(p, encoding="utf-8").read()
    active = [ln for ln in t.split("\n") if re.match(r"^\s*function\s+formatDate\s*\(", ln)]
    # also count 'formatDate(' usages, excluding commented lines and the utils file
    calls = [ln.strip() for ln in t.split("\n") if "formatDate(" in ln and "function formatDate" not in ln]
    print("  %s  active_def=%d  call_lines=%d" % (rel, len(active), len(calls)))
