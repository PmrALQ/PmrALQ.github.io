"""步骤2: 用边缘周期性检测像素块尺寸(缩放倍数)与网格原点
原理: 像素画放大后, 所有色彩跳变都落在网格线上, 即位置 ≡ offset (mod scale)
      按模取边缘强度均值最大者即为正确 scale
"""
import numpy as np
from PIL import Image

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'

im = Image.open(PATH).convert('RGB')
A = np.asarray(im).astype(np.float32)
H, W, _ = A.shape
print(f'图片: {W}x{H}')

# 8 个主体 bbox (来自步骤1)
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


def edge_profiles(sub):
    """返回 (水平边缘强度 dx, 垂直边缘强度 dy)"""
    g = sub.mean(axis=2)
    dx = np.abs(np.diff(g, axis=1)).sum(axis=0)   # 长度 = w-1
    dy = np.abs(np.diff(g, axis=0)).sum(axis=1)   # 长度 = h-1
    return dx, dy


def best_period(profile, smin=6, smax=34):
    """按模取均值, 返回 [(scale, offset, score)] 降序"""
    out = []
    n = len(profile)
    for s in range(smin, smax + 1):
        best = (-1.0, 0)
        for off in range(s):
            idx = np.arange(off, n, s)
            if len(idx) < 3:
                continue
            v = profile[idx].mean()
            if v > best[0]:
                best = (v, off)
        out.append((s, best[1], best[0]))
    out.sort(key=lambda t: -t[2])
    return out


print('\n=== 每个主体的 scale 候选 (前 4 名) ===')
results = {}
for name, (x0, y0, x1, y1) in BOXES.items():
    sub = A[y0:y1 + 1, x0:x1 + 1]
    dx, dy = edge_profiles(sub)
    rx = best_period(dx)
    ry = best_period(dy)
    results[name] = (rx, ry)
    print(f'\n[{name}]  bbox {x1-x0+1}x{y1-y0+1}')
    print('  水平(列方向): ' + ' | '.join(f's={s} off={o} score={v:.1f}' for s, o, v in rx[:4]))
    print('  垂直(行方向): ' + ' | '.join(f's={s} off={o} score={v:.1f}' for s, o, v in ry[:4]))

# 汇总: 多数主体共同的 scale 最可能是真实值
from collections import Counter
cand = Counter()
for name, (rx, ry) in results.items():
    cand[rx[0][0]] += 1
    cand[ry[0][0]] += 1
print('\n=== 各主体首选 scale 的分布 ===')
print(dict(cand.most_common()))
