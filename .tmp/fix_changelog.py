# -*- coding: utf-8 -*-
"""Targeted fixup for ChangelogEntry.vue: comment out local formatDate def,
update call site with options, trim now-unused destructure. Idempotent.
"""
import re

PATH = r"D:\self_website\components\ChangelogEntry.vue"

with open(PATH, "rb") as f:
    raw = f.read()
txt = raw.decode("utf-8")
orig = txt

# --- 1. update the template call site -------------------------------------
old_call = "{{ formatDate(entry.date) }}"
new_call = "{{ formatDate(entry.date, { month: 'long' }) }}"
n = txt.count(old_call)
if n == 1:
    txt = txt.replace(old_call, new_call)
    print("[OK] call site updated")
elif n == 0 and new_call in txt:
    print("[OK] call site already updated")
elif n > 1:
    raise SystemExit("[FAIL] call %r appears %d times" % (old_call, n))
else:
    raise SystemExit("[FAIL] call %r not found" % old_call)

# --- 2. comment out the local function def (if still active) ---------------
func_re = re.compile(
    r"^(\s*)function\s+formatDate\(dateStr\s*:\s*string\)\s*:\s*string\s*\{(?:(?!^\s*\}\s*$).)*?^\s*\}\s*$",
    re.MULTILINE,
)
m = func_re.search(txt)
if m:
    block = m.group(0)
    lines = block.split("\n")
    commented = ["/*"]
    commented.append(" * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），此处保留原始实现仅供回溯。")
    for ln in lines:
        commented.append(" *" + ((" " + ln) if ln.strip() else ""))
    commented.append(" */")
    txt = txt[: m.start()] + "\n".join(commented) + txt[m.end() :]
    print("[OK] def commented")

# --- 3. handle now-unused destructure --------------------------------------
# only if the destructure line no longer has any locale reference after the def
usei18n_re = re.compile(
    r"^(\s*)const\s*\{\s*([^}]*?)\s*\}\s*=\s*useI18n\(\)\s*$",
    re.MULTILINE,
)
m = usei18n_re.search(txt)
if m:
    ind, inner = m.group(1), m.group(2)
    names = [x.strip() for x in inner.split(",") if x.strip()]
    body_without_def = txt  # def already commented
    # count uses of each name outside the destructure line itself
    keep = []
    for name in names:
        body = "\n".join(txt.split("\n")[: m.start()] + txt.split("\n")[m.end():])
        uses = len(re.findall(r"\b" + re.escape(name) + r"\b", body))
        if uses > 0:
            keep.append(name)
    if set(keep) != set(names):
        new_inner = ", ".join(keep)
        new_line = "const { " + new_inner + " } = useI18n()" if keep else ""
        txt = txt[: m.start()] + "// " + txt[m.start() : m.end()] + "  // 原解构项已随 formatDate 抽离\n" + (new_line + "\n" if new_line else "") + txt[m.end():]
        print("[OK] useI18n destructure trimmed: %s -> %s" % (names, keep or "none"))
    else:
        print("[OK] destructure untouched")
else:
    print("[OK] no useI18n destructure found")

# --- write back ------------------------------------------------------------
if txt == orig:
    print("[NOOP] no changes")
else:
    with open(PATH, "wb") as f:
        f.write(txt.encode("utf-8"))
    print("[WROTE] ChangelogEntry.vue")
