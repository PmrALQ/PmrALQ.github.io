"""步骤1: 分析参考精灵表结构
- 定位 8 个主体(非白)区域
- 测出像素块尺寸(原生像素分辨率)
- 统计真实调色板
"""
from PIL import Image
import sys

PATH = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'

im = Image.open(PATH).convert('RGB')
W, H = im.size
print(f'图片尺寸: {W} x {H}')
px = im.load()


def is_bg(c):
    """接近白且低饱和 => 视为背景"""
    r, g, b = c
    return min(r, g, b) > 232 and (max(r, g, b) - min(r, g, b)) < 18


# 从四边泛洪, 标记外部背景
from collections import deque

bg = [[False] * W for _ in range(H)]
dq = deque()
for x in range(W):
    for y in (0, H - 1):
        if is_bg(px[x, y]) and not bg[y][x]:
            bg[y][x] = True
            dq.append((x, y))
for y in range(H):
    for x in (0, W - 1):
        if is_bg(px[x, y]) and not bg[y][x]:
            bg[y][x] = True
            dq.append((x, y))
while dq:
    x, y = dq.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and not bg[ny][nx] and is_bg(px[nx, ny]):
            bg[ny][nx] = True
            dq.append((nx, ny))

# 主体 = 非外部背景
sub = [[not bg[y][x] for x in range(W)] for y in range(H)]

# 连通域
lbl = [[0] * W for _ in range(H)]
blobs = []
cur = 0
for sy in range(H):
    for sx in range(W):
        if sub[sy][sx] and lbl[sy][sx] == 0:
            cur += 1
            dq = deque([(sx, sy)])
            lbl[sy][sx] = cur
            minx = maxx = sx
            miny = maxy = sy
            n = 0
            while dq:
                x, y = dq.popleft()
                n += 1
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and sub[ny][nx] and lbl[ny][nx] == 0:
                        lbl[ny][nx] = cur
                        dq.append((nx, ny))
            blobs.append({'id': cur, 'n': n, 'box': (minx, miny, maxx, maxy)})

blobs.sort(key=lambda b: -b['n'])
print(f'\n连通域总数: {len(blobs)}')
print('\n=== 最大的 12 个连通域 ===')
for b in blobs[:12]:
    x0, y0, x1, y1 = b['box']
    print(f"  #{b['id']:>3}  像素={b['n']:>7}  bbox=({x0},{y0})-({x1},{y1})  尺寸={x1-x0+1}x{y1-y0+1}")

# 对最大 8 个, 测像素块尺寸: 取每个 bbox 内的水平游程
print('\n=== 像素块尺寸探测 (在每个 bbox 内统计同色水平游程的最小公约) ===')
import math
from collections import Counter

sizes = []
for b in blobs[:8]:
    x0, y0, x1, y1 = b['box']
    runs = []
    for y in range(y0, y1 + 1):
        run = 1
        for x in range(x0 + 1, x1 + 1):
            if px[x, y] == px[x - 1, y]:
                run += 1
            else:
                runs.append(run)
                run = 1
        runs.append(run)
    c = Counter(r for r in runs if r > 1)
    common = c.most_common(6)
    g = 0
    for r, _ in common:
        g = math.gcd(g, r)
    print(f"  bbox({x0},{y0}) 常见游程={common}  => 公因数={g}")
    sizes.append(g)

# 全图调色板(仅主体内像素)
pal = Counter()
for y in range(H):
    for x in range(W):
        if sub[y][x]:
            pal[px[x, y]] += 1
print('\n=== 主体内出现最多的 16 种颜色(未量化, JPEG 原始值) ===')
for c, n in pal.most_common(16):
    print(f'  #{c[0]:02X}{c[1]:02X}{c[2]:02X}  {n:>7}')
print(f'\n主体像素总数: {sum(pal.values())}')
