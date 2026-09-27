# -*- coding: utf-8 -*-
"""
P0-2 只读状态检查(不修改任何源码文件):
  1) git status --short 与 git diff --stat,记录到 .tmp/PROGRESS.md
  2) 8 个目标文件的 formatDate 注释块结构检查(重复注释头 / 多余 '*/')
  3) 全局 formatDate 扫描(排除 .git / node_modules / .nuxt / .output / dist)
     - 列出所有出现位置
     - 检查是否存在非 utils/date.ts 的 active 定义
输出: .tmp/p02_check.txt
"""
import subprocess
import re
import sys
import datetime
from pathlib import Path

ROOT = Path(r"D:/self_website")
TMP = ROOT / ".tmp"
OUT = TMP / "p02_check.txt"
PYTHON = r"C:/Users/LWHM/.workbuddy/binaries/python/versions/3.13.12/python.exe"

ALL_TARGETS = [
    "components/ArchiveTimeline.vue",
    "components/BlogCard.vue",
    "components/BlogList.vue",
    "components/ChangelogEntry.vue",
    "components/ProjectCard.vue",
    "pages/blog/[slug].vue",
    "pages/gallery/index.vue",
    "pages/projects/[slug].vue",
]

EXCLUDE_DIRS = {".git", "node_modules", ".nuxt", ".output", "dist",
                ".vscode", "coverage", ".idea", "cache", ".cache"}
CODE_SUFFIX = {".ts", ".vue", ".js", ".mjs", ".cjs"}
SKIP_FILES = {"p02_check.py"}

MARKER = "原 formatDate 函数已抽离至"
DEFN_RE = re.compile(
    r"(?:export\s+)?(?:default\s+)?(?:function\s+formatDate\b|"
    r"(?:const|let|var)\s+formatDate\s*=)"
)
IMPORT_RE = re.compile(r"from\s+['\"][^'\"]*utils/date['\"]")


def git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        out = r.stdout.strip()
        err = r.stderr.strip()
        return out + (("\n[stderr] " + err) if err else "")
    except Exception as e:
        return f"[git 调用失败] {e}"


def check_block_health(name: str, text: str) -> list[str]:
    """检查单个文件中的 formatDate 迁移注释块结构。"""
    lines = text.split("\n")
    problems = []
    marker_rows = [i + 1 for i, ln in enumerate(lines) if MARKER in ln]
    if len(marker_rows) > 1:
        problems.append(f"{name}: 注释头出现 {len(marker_rows)} 次(行 {marker_rows}),应仅 1 次")
    if marker_rows:
        start = marker_rows[0] - 1
        block_start = None
        for j in range(start, -1, -1):
            if lines[j].strip() == "/*":
                block_start = j
                break
        if block_start is None:
            problems.append(f"{name}: 未找到注释块起始 /*")
        else:
            closes = 0
            close_rows = []
            for j in range(block_start, min(len(lines), block_start + 30)):
                if lines[j].strip() == "*/":
                    closes += 1
                    close_rows.append(j + 1)
            if closes > 1:
                problems.append(f"{name}: 注释块有 {closes} 个 '*/' 结束符(行 {close_rows}),应仅 1 个")
    return problems


def main() -> None:
    report = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report.append("=" * 66)
    report.append(f"P0-2 只读检查报告  {now}")
    report.append(f"工作目录: {ROOT}")
    report.append("=" * 66)

    # ---- 1. git 状态 ----
    report.append("\n### 1) git status --short")
    s = git("status", "--short")
    report.append(s if s else "(工作区干净)")
    report.append("\n### 2) git diff --stat")
    d = git("diff", "--stat")
    report.append(d if d else "(无未提交改动)")

    # ---- 2. 8 个目标文件注释块健康检查 ----
    report.append("\n### 3) 8 个目标文件注释块健康检查")
    any_problem = False
    for name in ALL_TARGETS:
        p = ROOT / name
        if not p.exists():
            report.append(f"  [缺失] {name}")
            any_problem = True
            continue
        text = p.read_text(encoding="utf-8")
        if MARKER not in text:
            report.append(f"  [无迁移注释] {name}")
            continue
        problems = check_block_health(name, text)
        if problems:
            any_problem = True
            for pr in problems:
                report.append(f"  [异常] {pr}")
        else:
            report.append(f"  [OK] {name}: 注释块结构完好")

    # ---- 3. 全局 formatDate 扫描 ----
    report.append("\n### 4) 全局 formatDate 出现位置(排除 .git/node_modules/.nuxt/.output/dist)")
    defn_found = False
    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in CODE_SUFFIX:
            continue
        if p.name in SKIP_FILES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "formatDate" not in text:
            continue
        rel = str(p.relative_to(ROOT))
        is_utils = rel == "utils/date.ts"
        n = len(re.findall(r"formatDate", text))
        import_ok = bool(IMPORT_RE.search(text))
        defn = DEFN_RE.search(text)
        tag = ""
        if defn:
            if not is_utils:
                tag = "  <-- 非 utils/date.ts 的 ACTIVE 定义"
                defn_found = True
        imp = " import-ok" if import_ok else ""
        report.append(f"  {rel}: formatDate x{n}{imp}{tag}")

    report.append("\n" + "=" * 66)
    if any_problem or defn_found:
        report.append("结论: P0-2 仍需修复(存在结构问题)")
    else:
        report.append("结论: P0-2 已完成,无需修复")
    report.append("=" * 66)

    TMP.mkdir(exist_ok=True)
    OUT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))

    # ---- 更新 PROGRESS.md ----
    progress_file = TMP / "PROGRESS.md"
    entry = [
        "",
        f"## P0-2 检查记录 {now}(只读)",
        "",
        "- git status --short:",
        "```",
        s if s else "(clean)",
        "```",
        "- git diff --stat:",
        "```",
        d if d else "(no diff)",
        "```",
        "- 检查结论: " + ("P0-2 仍需修复" if any_problem or defn_found else "P0-2 已完成,无需修复"),
        "- 检查详情见 {OUT}",
        "",
    ]
    with progress_file.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(entry))


if __name__ == "__main__":
    main()
