"""列出关键源文件的修改时间，用于划分版本区间"""
from pathlib import Path
import datetime

ROOT = Path(__file__).resolve().parent.parent
targets = []
for pat in ('components/*.vue', 'composables/*.ts', 'pages/**/*.vue', 'layouts/*.vue',
            'assets/css/*.css', 'nuxt.config.ts', 'content.config.ts', 'tailwind.config.js',
            'utils/*.ts', 'server/**/*.ts', 'scripts/*.py', 'public/cursors/*.png',
            'i18n/*.json', 'content/zh/**/*.md'):
    targets += list(ROOT.glob(pat))

rows = []
for p in targets:
    try:
        m = p.stat().st_mtime
        rows.append((m, p.relative_to(ROOT).as_posix()))
    except OSError:
        pass

rows.sort()
print(f'共 {len(rows)} 个文件\n')
print('=== 按修改时间排序 ===')
cur = None
for m, rel in rows:
    d = datetime.datetime.fromtimestamp(m).strftime('%Y-%m-%d %H:%M')
    day = d[:10]
    if day != cur:
        print(f'\n--- {day} ---')
        cur = day
    print(f'  {d}  {rel}')
