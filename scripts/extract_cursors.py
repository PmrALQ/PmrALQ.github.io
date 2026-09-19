"""严格提取: 按参考图逐图标还原真实色块, 去除白底, 只保留主体
产出:
  1) master/  原生分辨率透明 PNG (最忠实, 供存档/核对)
  2) public/cursors/  40×40 画布透明 PNG, 两套:
       {name}.png       日间套 —— 参考图原色(蓝)
       {name}-dark.png  夜间套 —— 色相 -25° 旋到青色, 对齐深色主题 --accent #00FFFF
     对应 main.css 的 :root / .dark 两套 --cur-* 变量
  3) 热点坐标表
原则:
  - 逐图标独立取色(各图配色并不统一), 不做全局统一
  - 白底透明; 主体内部被包围的白色(外链方框内部/沙漏玻璃)保留为不透明
  - 不做任何美化/加背景/加装饰
"""
import numpy as np
from PIL import Image
from collections import Counter, deque
from pathlib import Path
import colorsys

SRC = r'C:\Users\LWHM\.workbuddy\clipboard-images\clipboard-2026-09-19T11-49-50-148Z-f72df382.jpg'
ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / 'project-report' / 'extract' / 'master'
BACKUP = ROOT / 'project-report' / 'extract' / 'backup-v3'
OUT = ROOT / 'public' / 'cursors'
for d in (MASTER, BACKUP, OUT):
    d.mkdir(parents=True, exist_ok=True)

CANVAS = 40          # 光标画布尺寸
# v4.2 由 32 调到 40：32 与系统默认光标(Windows 32px)同尺寸, 用户感知不到差别;
# 40 ≈ 默认的 1.25 倍, 比默认略大但不夸张 (v4.1 曾为 32, v4 曾为 64)
# 注意: 改画布尺寸后必须同步更新 main.css 的热点, 并给 url() 加 ?v= 版本号破缓存
THR = 12             # 蓝色度阈值 B-R

A = np.asarray(Image.open(SRC).convert('RGB')).astype(np.int16)
H, W, _ = A.shape
R, G, B = A[:, :, 0], A[:, :, 1], A[:, :, 2]

mask = (B - R) > THR

# ---- 孔洞填充: 主体内部被包围的白色要保留 ----
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


def build_palette(pixels, max_colors=6, merge_dist=30, min_share=0.008):
    """从该图标的像素里提取真实平面色板(众数 + 邻近合并)"""
    q = (pixels // 8) * 8 + 4
    cnt = Counter(tuple(int(v) for v in row) for row in q)
    total = len(pixels)
    cands = []
    for c, n in cnt.most_common(60):
        arr = np.array(c, dtype=np.float32)
        for item in cands:
            if np.linalg.norm(item['c'] - arr) < merge_dist:
                w0, w1 = item['n'], n
                item['c'] = (item['c'] * w0 + arr * w1) / (w0 + w1)
                item['n'] += n
                break
        else:
            cands.append({'c': arr, 'n': n})
    cands.sort(key=lambda i: -i['n'])
    keep = [i for i in cands if i['n'] / total >= min_share][:max_colors]
    if not keep:
        keep = cands[:max_colors]
    return np.array([i['c'] for i in keep], dtype=np.float32)


HUE_SHIFT_DARK = -25   # 夜间套色相旋转(度)。参考图主色相 ≈207°(蓝) → 182°(青),
#                        对齐深色主题主题色 #00FFFF 的青色家族; 保留原明度/饱和度层次
#                        日间套不旋转(=0), 保持参考图原本的蓝色
# 产物约定: {name}.png = 日间(蓝)   {name}-dark.png = 夜间(青)
# 正好对应 main.css 的 :root / .dark 两套 --cur-* 变量, URL 无需改动


def shift_hue(rgba, deg):
    """只对不透明像素做 HSL 色相旋转, 保留明度与饱和度"""
    out = rgba.copy()
    ys, xs = np.nonzero(rgba[:, :, 3] > 0)
    delta = deg / 360.0
    for y, x in zip(ys, xs):
        r, g, b = rgba[y, x, :3] / 255.0
        h, l, s = colorsys.rgb_to_hls(float(r), float(g), float(b))
        h = (h + delta) % 1.0
        r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
        out[y, x, :3] = [round(r2 * 255), round(g2 * 255), round(b2 * 255)]
    return out


def fill_enclosed(mask2d):
    """把「不与边缘连通」的 False 区域补为 True（回填主体内部镂空）"""
    hh, ww = mask2d.shape
    out = np.zeros((hh, ww), dtype=bool)
    dq2 = deque()
    for x in range(ww):
        for y in (0, hh - 1):
            if not mask2d[y, x] and not out[y, x]:
                out[y, x] = True; dq2.append((x, y))
    for y in range(hh):
        for x in (0, ww - 1):
            if not mask2d[y, x] and not out[y, x]:
                out[y, x] = True; dq2.append((x, y))
    while dq2:
        x, y = dq2.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < ww and 0 <= ny < hh and not mask2d[ny, nx] and not out[ny, nx]:
                out[ny, nx] = True; dq2.append((nx, ny))
    return ~out & ~mask2d        # 被包围的空洞


results = {}
for name, (x0, y0, x1, y1) in BOXES.items():
    sub_rgb = A[y0:y1 + 1, x0:x1 + 1]
    m = subj[y0:y1 + 1, x0:x1 + 1]
    h, w, _ = sub_rgb.shape

    pal = build_palette(sub_rgb[m])
    # 最近色吸附
    flat = sub_rgb.reshape(-1, 3).astype(np.float32)
    d = ((flat[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    idx = d.argmin(axis=1)
    snapped = pal[idx].round().astype(np.uint8).reshape(h, w, 3)

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = snapped
    # 去除抗锯齿白晕: 吸附后仍是近白的像素, 若不属于「内部孔洞」则判为背景
    # (主体内部真正被包围的白色会保留, 例如外链小方框内部、沙漏玻璃)
    lum = snapped.astype(np.int32).sum(axis=2)
    near_white = lum > 690
    solid = m & (holes[y0:y1 + 1, x0:x1 + 1] | ~near_white)
    # 内部孔洞回填: 修掉白晕剔除 + 降采样造成的镂空
    enclosed = fill_enclosed(solid)
    solid = solid | enclosed
    rgba[:, :, 3] = np.where(solid, 255, 0).astype(np.uint8)

    master = Image.fromarray(rgba, 'RGBA')
    master.save(MASTER / f'{name}.png')

    # 缩放到 64×64 画布(等比, 居中偏左上留白少), 用 LANCZOS 保留平面色
    scale = CANVAS / max(w, h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    small = master.resize((nw, nh), Image.LANCZOS)
    # 再吸附一次, 消除缩放产生的中间色
    arr = np.asarray(small).astype(np.float32)
    rgb = arr[:, :, :3].reshape(-1, 3)
    al = arr[:, :, 3].reshape(-1)
    dd = ((rgb[:, None, :] - pal[None, :, :]) ** 2).sum(axis=2)
    rgb2 = pal[dd.argmin(axis=1)].round().astype(np.uint8)
    arr2 = np.zeros((nh, nw, 4), dtype=np.uint8)
    arr2[:, :, :3] = rgb2.reshape(nh, nw, 3)
    arr2[:, :, 3] = np.where(al > 110, 255, 0).astype(np.uint8).reshape(nh, nw)

    canvas = np.zeros((CANVAS, CANVAS, 4), dtype=np.uint8)
    ox, oy = (CANVAS - nw) // 2, (CANVAS - nh) // 2
    canvas[oy:oy + nh, ox:ox + nw] = arr2
    # 画布层再回填一次: 修掉降采样阈值造成的细小镂空(颜色已在 arr2 中就位)
    encl2 = fill_enclosed(canvas[:, :, 3] > 0)
    canvas[encl2, 3] = 255
    # 日间套: 参考图原色(蓝), 不旋转
    Image.fromarray(canvas, 'RGBA').save(OUT / f'{name}.png')
    # 夜间套: 色相旋到青色家族, 对齐深色主题 #00FFFF; 热点与日间完全一致
    dark = shift_hue(canvas, HUE_SHIFT_DARK)
    Image.fromarray(dark, 'RGBA').save(OUT / f'{name}-dark.png')

    # 热点: 依据造型语义, 从 alpha 计算
    al2 = canvas[:, :, 3] > 0
    ys, xs = np.nonzero(al2)
    if name in ('arrow', 'external'):
        # 箭头左边缘自尖端起始: 取最左一列中的最上像素 = 尖端
        # (外链图标的方框在右侧, 不会干扰最左列)
        lx = xs.min()
        hx = int(lx); hy = int(ys[xs == lx].min())
    elif name == 'hand':
        ty = ys.min(); hx = xs[ys == ty].min(); hy = ty          # 食指尖
    elif name in ('zoom', 'zoom-out'):
        by = ys.max(); hx = xs[ys == by].min(); hy = by          # 手柄末端(最下最左)
    else:
        hx = int((xs.min() + xs.max()) / 2); hy = int((ys.min() + ys.max()) / 2)
    results[name] = {'hot': (int(hx), int(hy)), 'native': (w, h), 'canvas_size': (nw, nh),
                     'offset': (ox, oy), 'palette': pal.round().astype(int).tolist()}

print('=== 提取结果 ===')
for name, r in results.items():
    pal = ' '.join(f'#{c[0]:02X}{c[1]:02X}{c[2]:02X}' for c in r['palette'])
    print(f"{name:12s} 原生 {r['native'][0]}x{r['native'][1]} -> 画布内 {r['canvas_size'][0]}x{r['canvas_size'][1]}"
          f" @({r['offset'][0]},{r['offset'][1]})  热点={r['hot']}")
    print(f'             色板: {pal}')

print('\n=== CSS 热点表 (64×64 画布坐标系) ===')
for name, r in results.items():
    print(f'  {name:12s} {r["hot"][0]} {r["hot"][1]}')

import json
(ROOT / 'project-report' / 'extract' / 'hotspots.json').write_text(
    json.dumps({k: {'hot': v['hot'], 'palette': v['palette']} for k, v in results.items()},
               ensure_ascii=False, indent=2), encoding='utf-8')
print('\nmaster ->', MASTER)
print('cursor ->', OUT)
