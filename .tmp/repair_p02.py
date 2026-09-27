# -*- coding: utf-8 -*-
"""
P0-2 修复：归一化 formatDate 抽离注释块（去除重复注释头与多余 */），
并对 8 个目标文件做一次性校验。
"""
import re
from pathlib import Path

ROOT = Path('D:/self_website')
TARGETS = [
    'components/ArchiveTimeline.vue',
    'components/BlogCard.vue',
    'components/BlogList.vue',
    'components/ChangelogEntry.vue',
    'components/ProjectCard.vue',
    'pages/blog/[slug].vue',
    'pages/gallery/index.vue',
    'pages/projects/[slug].vue',
]

HDR_A1 = ' * 原 formatDate 函数已抽离至 utils/date.ts（Nuxt 自动导入），'
HDR_A2 = ' * 此处保留原始实现供回溯。'
HDR_A3 = ' * 此处保留原始实现供撤回。'
FN_START = ' * function formatDate('


def normalize(text: str) -> tuple[str, bool]:
    crlf = '\r\n' in text
    lines = [ln[:-1] if ln.endswith('\r') else ln for ln in text.split('\n')]
    out: list[str] = []
    changed = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # 检测注释块起点：/* 后跟 HDR_A1
        if line.strip() == '/*' and i + 1 < n and lines[i + 1] == HDR_A1:
            # 找块内 body 起点（function formatDate 行）
            fn_idx = None
            for j in range(i + 1, n):
                if lines[j].startswith(FN_START):
                    fn_idx = j
                    break
                if lines[j].strip() == '*/':
                    break
            if fn_idx is None:
                out.append(line)
                i += 1
                continue
            # 找块结束：body 之后第一个 */ 行
            close_idx = None
            for j in range(fn_idx, n):
                if lines[j].strip() == '*/':
                    close_idx = j
                    break
            if close_idx is None:
                out.append(line)
                i += 1
                continue
            # 重建块：去重注释头 + body + 单一结束 */
            header: list[str] = []
            seen: set[str] = set()
            for j in range(i + 1, fn_idx):
                l = lines[j]
                if l not in seen:
                    seen.add(l)
                    header.append(l)
            rebuilt = ['/*'] + header + lines[fn_idx:close_idx + 1]
            if rebuilt != lines[i:close_idx + 1]:
                out.extend(rebuilt)
                changed = True
            else:
                out.extend(lines[i:close_idx + 1])
            i = close_idx + 1
        else:
            out.append(line)
            i += 1
    result = '\n'.join(out)
    if crlf:
        result = result.replace('\n', '\r\n')
    return result, changed


def scan_formatdate(root: Path) -> None:
    """扫描所有 .vue/.ts 文件中的 formatDate 出现，做最终体检。"""
    pat = re.compile(r'formatDate')
    defn = re.compile(r'(function formatDate|const formatDate\s*=|export function formatDate)')
    for p in sorted(root.rglob('*')):
        if p.suffix not in ('.vue', '.ts'):
            continue
        if any(part in ('.nuxt', '.output', 'node_modules', 'dist') for part in p.parts):
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        hits = pat.findall(text)
        if hits:
            defs = defn.findall(text)
            status = 'DEFINITION(未注释?)' if defs else 'used'
            print(f'  {p.relative_to(root)}: formatDate x{len(hits)} [{status}]')


if __name__ == '__main__':
    print('== 修复阶段 ==')
    for name in TARGETS:
        p = ROOT / name
        if not p.exists():
            print(f'SKIP(缺失): {name}')
            continue
        text = p.read_text(encoding='utf-8')
        new_text, changed = normalize(text)
        if changed:
            p.write_text(new_text, encoding='utf-8', newline='')
            print(f'FIXED: {name}')
        else:
            print(f'OK 无损坏注释块: {name}')

    print()
    print('== 全量扫描 formatDate ==')
    scan_formatdate(ROOT)

    print()
    print('== utils/date.ts ==')
    d = ROOT / 'utils/date.ts'
    if d.exists():
        print(d.read_text(encoding='utf-8'))
    else:
        print('缺失 utils/date.ts')
