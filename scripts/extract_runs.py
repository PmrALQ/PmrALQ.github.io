"""步骤4: 先量化颜色, 再统计游程长度 => 块宽 = 游程的公约数
量化后再测, 避开 JPEG 噪声导致的「相邻像素不相等」
"""
import numpy as np
from PIL import Image

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'
im = Image.open(PATH).convert('RGB')
A = np.asarray(im)

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


def kmeans(img_flat, k=6, iters=12, seed=0):
    rng = np.random.default_rng(seed)
    c = img_flat[rng.choice(len(img_flat), k, replace=False)].astype(np.float32)
    for _ in range(iters):
        d = ((img_flat[:, None, :] - c[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for i in range(k):
            m = lab == i
            if m.sum() > 0:
                c[i] = img_flat[m].mean(axis=0)
    return c, lab


def run_lengths_1d(labels):
    """返回所有水平游程长度"""
    res = []
    for row in labels:
        start = 0
        for i in range(1, len(row)):
            if row[i] != row[start]:
                res.append(i - start)
                start = i
        res.append(len(row) - start)
    return res


def gcd_list(vals):
    from math import gcd
    g = 0
    for v in vals:
        g = gcd(g, v)
    return g


from collections import Counter

print('=== 量化后游程分析 (取每图前 3000 个最大像素做 kmeans) ===')
summary = {}
for name, (x0, y0, x1, y1) in BOXES.items():
    sub = A[y0:y1 + 1, x0:x1 + 1]
    h, w, _ = sub.shape
    flat = sub.reshape(-1, 3).astype(np.float32)
    # 为速度, 先把白色类排除? 不移除, 保留全部
    if len(flat) > 4000:
        idx = np.linspace(0, len(flat) - 1, 4000).astype(int)
        samp = flat[idx]
    else:
        samp = flat
    centers, _ = kmeans(samp, k=6)
    # 用全体像素归类
    d = ((flat[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    lab = d.argmin(axis=1).reshape(h, w)

    hr = run_lengths_1d(lab)                       # 水平游程
    vr = run_lengths_1d(lab.T)                     # 垂直游程
    ch = Counter(r for r in hr if 2 <= r <= 60)
    cv = Counter(r for r in vr if 2 <= r <= 60)
    topH = ch.most_common(6)
    topV = cv.most_common(6)
    # 候选块宽: 最常见游程值 及 全部游程的公约数
    candH = [r for r, _ in topH if r >= 3]
    candV = [r for r, _ in topV if r >= 3]
    gH = gcd_list(candH) if candH else 0
    gV = gcd_list(candV) if candV else 0
    summary[name] = (gH, gV, topH, topV)
    print(f'\n[{name}]  {w}x{h}')
    print(f'  水平游程 top6: {topH}   公约数={gH}')
    print(f'  垂直游程 top6: {topV}   公约数={gV}')

print('\n=== 汇总 ===')
for name, (gH, gV, _, _) in summary.items():
    print(f'  {name:12s} 水平块宽候选={gH}  垂直块宽候选={gV}')

print('\n=== 量化后的调色板 (每个主体) ===')
for name, (x0, y0, x1, y1) in BOXES.items():
    sub = A[y0:y1 + 1, x0:x1 + 1]
    flat = sub.reshape(-1, 3).astype(np.float32)
    q = Image.fromarray(sub).quantize(colors=6, method=Image.Quantize.MEDIANCUT)
    pal = np.asarray(q.getpalette())[:18].reshape(-1, 3)
    cnt = Counter(q.getdata())
    print(f'  [{name}]')
    for i, n in cnt.most_common(6):
        r, g, b = pal[i]
        print(f'      #{r:02X}{g:02X}{b:02X}  {n:>6}px')
