"""步骤3: 用「网格线 vs 非网格线」的边缘强度对比度检测真实缩放倍数
像素画放大后, 色彩跳变只发生在网格线上 => grid 位置边缘强度高, 非 grid 位置接近噪声底
metric = mean(d[grid]) / mean(d[non-grid]), 取最大
"""
import numpy as np
from PIL import Image

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'
im = Image.open(PATH).convert('RGB')
A = np.asarray(im).astype(np.float32)

BOXES = {
    'arrow':      (222, 179, 417, 445),
    'hand':       (1119, 158, 1239, 444),
    'text':       (624, 159, 860, 445),
    'external':   (1504, 155, 1741, 446),
    'zoom':       (181, 630, 449, 911),
    'zoom-out':   (597, 630, 868, 911),
    'wait':       (1074, 630, 1289, 922),
    'not-allowed': (1462, 630, 1741, 908),
}


def profiles(sub):
    g = sub.mean(axis=2)
    dx = np.abs(np.diff(g, axis=1)).sum(axis=0)
    dy = np.abs(np.diff(g, axis=0)).sum(axis=1)
    return dx, dy


def contrast(profile, smin=4, smax=40):
    n = len(profile)
    overall = profile.mean() + 1e-9
    out = []
    for s in range(smin, smax + 1):
        best = None
        for off in range(s):
            mask = (np.arange(n) - off) % s == 0
            if mask.sum() < 2 or (~mask).sum() < 2:
                continue
            on = profile[mask].mean()
            off_ = profile[~mask].mean() + 1e-9
            ratio = on / off_
            if best is None or ratio > best[0]:
                best = (ratio, off, on, off_)
        if best:
            out.append((s, best[1], best[0], best[2], best[3]))
    out.sort(key=lambda t: -t[2])
    return out, overall


print('=== 网格对比度检测 (ratio = 网格线边缘强度 / 非网格线边缘强度) ===')
consensus = {}
for name, (x0, y0, x1, y1) in BOXES.items():
    sub = A[y0:y1 + 1, x0:x1 + 1]
    dx, dy = profiles(sub)
    rx, ovx = contrast(dx)
    ry, ovy = contrast(dy)
    print(f'\n[{name}] {x1-x0+1}x{y1-y0+1}')
    print('  列方向 top5: ' + ' | '.join(f's={s} off={o} r={r:.2f}' for s, o, r, _, _ in rx[:5]))
    print('  行方向 top5: ' + ' | '.join(f's={s} off={o} r={r:.2f}' for s, o, r, _, _ in ry[:5]))
    consensus[name] = (rx[0], ry[0])

print('\n=== 汇总: 各主体列/行方向的最佳 scale 与比值 ===')
for name, (rx, ry) in consensus.items():
    print(f'  {name:12s} 列 s={rx[0]:>2} (r={rx[2]:.2f})   行 s={ry[0]:>2} (r={ry[2]:.2f})')

rs = [v[0][2] for v in consensus.values()] + [v[1][2] for v in consensus.values()]
print(f'\n所有最佳比值范围: {min(rs):.2f} ~ {max(rs):.2f}')
print('(若比值普遍接近 1.0~1.5, 说明该图并非严格网格放大的像素画, AI 生成块状不规则)')
