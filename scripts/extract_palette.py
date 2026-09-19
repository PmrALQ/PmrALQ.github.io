"""步骤6: 用众数法确定真实平面色板(不做 k-means, 避免抗锯齿过渡被聚成独立颜色)
把每个通道量化到 8 级(保留高位), 统计众数, 再按出现频次排序
"""
import numpy as np
from PIL import Image
from collections import Counter, deque

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'
A = np.asarray(Image.open(PATH).convert('RGB')).astype(np.int16)
H, W, _ = A.shape
R, G, B = A[:, :, 0], A[:, :, 1], A[:, :, 2]
mask = (B - R) > 12

# 孔洞填充
outside = np.zeros((H, W), dtype=bool)
dq = deque()
for x in range(W):
    for y in (0, H - 1):
        if not mask[y, x] and not outside[y, x]:
            outside[y, x] = True; dq.append((x, y))
for y in range(H):
    for x in (0, W - 1):
        if not mask[y, x] and not outside[y, x]:
            outside[y, x] = True; dq.append((x, y))
while dq:
    x, y = dq.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and not mask[ny, nx] and not outside[ny, nx]:
            outside[ny, nx] = True; dq.append((nx, ny))
holes = (~mask) & (~outside)
subj = mask | holes

BOXES = {
    'arrow':      (221, 179, 418, 446),
    'hand':       (624, 159, 861, 445),
    'text':       (1119, 158, 1239, 445),
    'external':   (1504, 155, 1742, 446),
    'zoom':       (180, 628, 450, 912),
    'zoom-out':   (596, 629, 868, 912),
    'wait':       (1073, 629, 1290, 923),
    'not-allowed': (1461, 629, 1742, 908),
}

sel = np.zeros((H, W), dtype=bool)
for (x0, y0, x1, y1) in BOXES.values():
    sel[y0:y1 + 1, x0:x1 + 1] = True
subj_sel = subj & sel

px = A[subj_sel]
# 量化到 8 级: value // 8 * 8 + 4
q = (px // 8) * 8 + 4
keys = [tuple(int(v) for v in row) for row in q]
cnt = Counter(keys)

print('=== 主体内最高频的 14 种量化色 (众数法) ===')
total = len(px)
for c, n in cnt.most_common(14):
    print(f'  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  {n:>7}px  {n*100/total:5.2f}%')

print('\n=== 合并邻近色后的「真实色板」候选 ===')
# 把高频色聚类(欧氏距离<28 视为同色), 用加权均值代表
cands = []
for c, n in cnt.most_common(40):
    arr = np.array(c, dtype=np.float32)
    merged = False
    for item in cands:
        if np.linalg.norm(item['c'] - arr) < 28:
            w0 = item['n']; w1 = n
            item['c'] = (item['c'] * w0 + arr * w1) / (w0 + w1)
            item['n'] += n
            merged = True
            break
    if not merged:
        cands.append({'c': arr, 'n': n})
cands.sort(key=lambda i: -i['n'])
for i, item in enumerate(cands[:8], 1):
    r, g, b = item['c'].round().astype(int)
    print(f'  {i}. #{r:02X}{g:02X}{b:02X}   {item["n"]:>7}px  {item["n"]*100/total:5.2f}%')

print('\n=== 逐图色板(每图 top6) ===')
for name, (x0, y0, x1, y1) in BOXES.items():
    m = subj[y0:y1 + 1, x0:x1 + 1]
    p = A[y0:y1 + 1, x0:x1 + 1]
    qq = (p[m] // 8) * 8 + 4
    kk = [tuple(int(v) for v in row) for row in qq]
    cc = Counter(kk)
    top = cc.most_common(6)
    s = '  '.join(f'#{c[0]:02X}{c[1]:02X}{c[2]:02X}({n*100/len(kk):.0f}%)' for c, n in top)
    print(f'  {name:12s} {s}')
