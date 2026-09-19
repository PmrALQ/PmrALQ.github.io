"""步骤5: 用「蓝色度 B-R」分割主体(避开近白误伤), 提取真实调色板
- 白底/灰色卡片边框: B-R ≈ 0  → 排除
- 蓝色主体 + 抗锯齿过渡: B-R 显著 → 保留
- 主体内部被包围的白色(外链小方框、沙漏玻璃): 用孔洞填充补回
"""
import numpy as np
from PIL import Image
from collections import Counter, deque

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'
im = Image.open(PATH).convert('RGB')
A = np.asarray(im).astype(np.int16)
H, W, _ = A.shape

R, G, B = A[:, :, 0], A[:, :, 1], A[:, :, 2]
blueness = B - R
print('蓝色度统计: min=%d max=%d' % (blueness.min(), blueness.max()))

THR = 12
mask = blueness > THR
print(f'mask(B-R>{THR}) 像素数: {mask.sum()}  ({mask.sum()*100/(H*W):.2f}%)')

# 连通域(8邻接)
lbl = np.zeros((H, W), dtype=np.int32)
comps = []
cur = 0
ys, xs = np.nonzero(mask)
visited = np.zeros((H, W), dtype=bool)
for sy, sx in zip(ys, xs):
    if visited[sy, sx]:
        continue
    cur += 1
    dq = deque([(sx, sy)])
    visited[sy, sx] = True
    minx = maxx = sx
    miny = maxy = sy
    n = 0
    while dq:
        x, y = dq.popleft()
        lbl[y, x] = cur
        n += 1
        minx = min(minx, x); maxx = max(maxx, x)
        miny = min(miny, y); maxy = max(maxy, y)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    dq.append((nx, ny))
    comps.append({'id': cur, 'n': n, 'box': (minx, miny, maxx, maxy)})

comps.sort(key=lambda c: -c['n'])
print(f'\n连通域总数: {len(comps)}')
print('\n=== 前 10 大连通域 ===')
for c in comps[:10]:
    x0, y0, x1, y1 = c['box']
    print(f"  #{c['id']:>3} px={c['n']:>6}  bbox=({x0},{y0})-({x1},{y1})  {x1-x0+1}x{y1-y0+1}")

# 8 个主要主体按位置命名
main = comps[:8]
def name_of(box):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    col = int(cx // (W / 4))
    row = int(cy // (H / 2))
    names = [['arrow', 'hand', 'text', 'external'],
             ['zoom', 'zoom-out', 'wait', 'not-allowed']]
    return names[min(row, 1)][min(col, 3)]

print('\n=== 8 个主体(按图内位置命名) ===')
named = {}
for c in main:
    nm = name_of(c['box'])
    x0, y0, x1, y1 = c['box']
    named[nm] = c
    print(f"  {nm:12s} px={c['n']:>6}  {x1-x0+1}x{y1-y0+1}")

# 孔洞填充: 从四边泛洪非mask, 未到达的非mask即为内部孔洞
filled = mask.copy()
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
            outside[ny, nx] = True
            dq.append((nx, ny))
holes = (~mask) & (~outside)
print(f'\n内部孔洞(需补回主体)像素数: {holes.sum()}')

# 真实调色板: 对「主体 ∪ 孔洞」内的像素做颜色聚类
subj = mask | holes
# 只看 8 个主体各自的 bbox 范围内, 避免杂点
sel = np.zeros((H, W), dtype=bool)
for c in main:
    x0, y0, x1, y1 = c['box']
    sel[y0:y1 + 1, x0:x1 + 1] = True
subj_sel = subj & sel
px = A[subj_sel].astype(np.float32)
print(f'参与调色板统计的像素: {len(px)}')

# k-means
def kmeans(X, k, iters=25, seed=1):
    rng = np.random.default_rng(seed)
    c = X[rng.choice(len(X), k, replace=False)].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - c[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for i in range(k):
            m = lab == i
            if m.sum() > 0:
                c[i] = X[m].mean(axis=0)
    return c, lab

for k in (5, 6, 7):
    centers, lab = kmeans(px, k)
    cnt = Counter(lab.tolist())
    print(f'\n=== k={k} 调色板 ===')
    for i in np.argsort([-cnt[j] for j in range(k)]):
        r, g, b = centers[i].round().astype(int)
        print(f'    #{r:02X}{g:02X}{b:02X}  {cnt[i]:>7}px  ({cnt[i]*100/len(px):.1f}%)')
