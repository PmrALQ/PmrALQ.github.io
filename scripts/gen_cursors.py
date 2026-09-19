"""
生成像素风蓝色鼠标光标（PNG）—— v3

v3 · 2026-09-16：画布由 24×24 升到 32×32（放大镜 / 沙漏才画得开，32 亦是
        浏览器不缩放的安全上限）；调色板换成参考精灵表的 5 色：
        亮色 K#0C1A5E 深海军蓝描边 · B#1E96F0 主蓝 · M#63C6F8 次级面/高光面
             L#B3E2FD 浅蓝面（沙漏玻璃 / 放大镜镜片）· W#FFFFFF 反光点
        暗色 K#F2F7FF · B#4FAEF5 · M#9BD8FB · L#D6EEFE · W 保持白色
        全部 8 款统一 32×32；8 个字符矩阵常量改为
        ARROW / POINTER / TEXT / ALIAS / ZOOM_IN / ZOOM_OUT / WAIT / NOT_ALLOWED。
        文件仍写入 public/cursors/，命名沿用既有约定（见 SHAPES 键），
        以保持 assets/css/main.css 的 --cur-* 变量与选择器不变。

纯标准库手写 PNG 编码（struct + zlib），无第三方依赖。

配色沿用「描边深、填充亮」的统一逻辑，保证亮/暗两种主题下都清晰。
热点见 HOTSPOTS，供 CSS `cursor: url(...) <x> <y>` 使用。
"""
import struct
import zlib
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'public' / 'cursors'
OUT.mkdir(exist_ok=True)

N = 32  # 统一 32×32 画布

# 5 色调色板（值 = (r, g, b[, a])；缺省 alpha = 255）
COLORS = {
    'light': {
        'K': (12, 26, 94),      # #0C1A5E 深海军蓝 描边
        'B': (30, 150, 240),    # #1E96F0 主蓝      主体填充
        'M': (99, 198, 248),    # #63C6F8 中蓝      次级面 / 高光面
        'L': (179, 226, 253),   # #B3E2FD 亮蓝      浅色面（玻璃 / 镜片）
        'W': (255, 255, 255),   # #FFFFFF 白        反光点 / 沙漏空隙
    },
    'dark': {
        'K': (242, 247, 255),   # #F2F7FF 近白      描边（深底上反转为浅色）
        'B': (79, 174, 245),    # #4FAEF5 主蓝
        'M': (155, 216, 251),   # #9BD8FB 中蓝
        'L': (214, 238, 254),   # #D6EEFE 亮蓝
        'W': (255, 255, 255),   # #FFFFFF 白
    },
}

# 各光标热点（对应 32×32 PNG 像素坐标），与 assets/css/main.css 的 cursor 规则一致
HOTSPOTS = {
    'arrow':       (1, 1),    # 左上尖端
    'hand':        (5, 2),    # 食指指尖
    'text':        (16, 16),  # 画面中心（竖笔中部）
    'external':    (1, 1),    # 与 arrow 一致，角标不改变点击原点
    'zoom':        (6, 27),   # 放大镜手柄末端（左下）
    'zoom-out':    (6, 27),   # 同上
    'wait':        (16, 16),  # 中心
    'not-allowed': (16, 16),  # 中心
}


# ---------- 基础网格工具 ----------
def blank(n=N):
    return [['.'] * n for _ in range(n)]


def disc(g, cx, cy, r, ch):
    """实心圆"""
    for y in range(len(g)):
        for x in range(len(g[0])):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                g[y][x] = ch


def ring(g, cx, cy, r_out, r_in, ch):
    """圆环（r_in < d <= r_out）"""
    for y in range(len(g)):
        for x in range(len(g[0])):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if r_in * r_in < d2 <= r_out * r_out:
                g[y][x] = ch


def bar(g, x0, y0, x1, y1, t, ch):
    """等宽斜条：点到线段的距离 <= t/2"""
    for y in range(len(g)):
        for x in range(len(g[0])):
            dx, dy = x1 - x0, y1 - y0
            l2 = dx * dx + dy * dy
            if l2 == 0:
                d = math.hypot(x - x0, y - y0)
            else:
                u = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / l2))
                d = math.hypot(x - (x0 + u * dx), y - (y0 + u * dy))
            if d <= t / 2:
                g[y][x] = ch


def rect(g, x0, y0, x1, y1, ch):
    """实心矩形（含端点，整数坐标）"""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            if 0 <= y < len(g) and 0 <= x < len(g[0]):
                g[y][x] = ch


def to_matrix(g):
    return [''.join(row) for row in g]


def pad_matrix(matrix, n=N):
    """把矩阵补齐到 n×n（右补透明列、下补透明行）"""
    out = [r.ljust(n, '.') for r in matrix]
    while len(out) < n:
        out.append('.' * n)
    return out[:n]


def overlay(base, patch, ox, oy):
    """把 patch 叠加到 base 的 (ox, oy) 处，'.' 视为透明"""
    out = [list(r.ljust(N, '.')) for r in base]
    for y, row in enumerate(patch):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            if 0 <= oy + y < len(out) and 0 <= ox + x < len(out[0]):
                out[oy + y][ox + x] = ch
    return to_matrix(out)


def despeckle(g, min_neighbors=1):
    """剔除孤立像素凸起——圆环光栅化会在正方向留出单格毛刺"""
    n = len(g)
    out = [row[:] for row in g]
    for y in range(n):
        for x in range(n):
            if g[y][x] == '.':
                continue
            cnt = 0
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and g[ny][nx] != '.':
                    cnt += 1
            if cnt < min_neighbors:
                out[y][x] = '.'
    return out


def check(matrix, n=N, allow=('.', 'K', 'B', 'M', 'L', 'W')):
    """校验矩阵尺寸与字符合法性，早失败早发现"""
    assert len(matrix) == n, f'行数应为 {n}，实为 {len(matrix)}'
    for i, row in enumerate(matrix):
        assert len(row) == n, f'第 {i} 行宽度应为 {n}，实为 {len(row)}'
        bad = set(row) - set(allow)
        assert not bad, f'第 {i} 行含非法字符 {bad}'
    return matrix


# ---------- 几何光栅化（箭头轮廓：斜边严格 45°、凹口无孤立像素） ----------
def raster(verts, n=N):
    """扫描线光栅化多边形 → inside 布尔矩阵（按像素中心 x+0.5, y+0.5 取样）"""
    inside = [[False] * n for _ in range(n)]
    m = len(verts)
    for y in range(n):
        cy = y + 0.5
        xs = []
        for i in range(m):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % m]
            if (y1 <= cy) != (y2 <= cy):
                t = (cy - y1) / float(y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            a, b = xs[k], xs[k + 1]
            for x in range(n):
                if a <= x + 0.5 <= b:
                    inside[y][x] = True
    return inside


def outline_of(inside, n=N, width=1):
    """栅格外描边：与「图形外」像素相邻的图形内像素。
    width=1 → 四邻域（1px）；width>=2 → 追加对角邻域（≈2px 视觉粗细）"""
    offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if width >= 2:
        offsets += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    out = [[False] * n for _ in range(n)]
    for y in range(n):
        for x in range(n):
            if not inside[y][x]:
                continue
            for dx, dy in offsets:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= n or ny >= n or not inside[ny][nx]:
                    out[y][x] = True
                    break
    return out


def fill_mask(mask, outline_w=1):
    """布尔 inside 蒙版 → 字符网格：轮廓填 K、内部填 B"""
    outline = outline_of(mask, N, outline_w)
    g = blank()
    for y in range(N):
        for x in range(N):
            if mask[y][x]:
                g[y][x] = 'K' if outline[y][x] else 'B'
    return g


def fill_poly(verts, outline_w=2):
    """多边形 → 字符网格：轮廓填 K、内部填 B"""
    return fill_mask(raster(verts), outline_w)


def outline_chars(g, width=1):
    """对已着色的字符网格按轮廓重描 K（不动内部填充色）"""
    mask = [[c != '.' for c in row] for row in g]
    out = outline_of(mask, len(g), width)
    for y in range(len(g)):
        for x in range(len(g[0])):
            if out[y][x]:
                g[y][x] = 'K'
    return g


def rim_light(g, ch='M'):
    """沿图形内侧右缘描 1px 高光面（读作受光侧）：跳过右缘 K 描边，
    落在最外侧的填充像素上，使高光成为连续的一条亮边而非零散点"""
    n = len(g)
    for y in range(n):
        x = n - 1
        while x >= 0 and g[y][x] == '.':
            x -= 1
        while x >= 0 and g[y][x] == 'K':   # 跳过右缘描边
            x -= 1
        if x >= 0 and g[y][x] == 'B':
            g[y][x] = ch
    return g


# ---------- ① ARROW：默认指针（斜箭头，尖端左上） ----------
# 轮廓（顺时针闭合）：尖端 (1,1) → 右翼尖 (16,16)【斜边严格 45°】
#   → 沿头部下缘回行至尾右上 (11,16) → 锥形尾右下 (7,29)
#   → 尾左下 (1,29) → 头部左缘 (1,29)-(1,1) 垂直共线（无左侧凹口）→ 闭合
# 热点：(1,1) 左上尖端
ARROW_POLY = [(1, 1), (16, 16), (11, 16), (7, 29), (1, 29)]

ARROW = check(to_matrix(rim_light(fill_poly(ARROW_POLY, outline_w=2))))


# ---------- ② POINTER：手型（食指朝上、其余三指握拳，指尖在左上） ----------
def make_pointer():
    """食指竖直高耸 + 右侧三根蜷曲手指的指节阶梯 + 左侧拇指 + 圆润手掌。
    各部件刻意加宽并相互重叠，保证 2px 描边后仍有填充、且无断裂缝隙。"""
    g = blank()
    # 食指（竖直，指向左上）
    rect(g, 3, 5, 8, 19, 'X')
    disc(g, 5.5, 5.0, 3.6, 'X')
    # 三根蜷曲手指的指节：自食指向右、逐节下沉，形成斜向的指背
    disc(g, 12.0, 14.0, 5.0, 'X')
    disc(g, 15.5, 17.0, 4.6, 'X')
    disc(g, 18.5, 20.0, 4.0, 'X')
    # 手掌主体
    rect(g, 4, 13, 19, 24, 'X')
    disc(g, 12.0, 23.0, 6.8, 'X')
    # 拇指（左侧外凸）
    disc(g, 2.5, 19.0, 3.8, 'X')
    mask = [[c != '.' for c in row] for row in g]
    return to_matrix(despeckle(rim_light(fill_mask(mask, outline_w=2)), 2))


# 热点：(5,2) 食指指尖
POINTER = check(make_pointer())


# ---------- ③ TEXT：文本 I 型（上下横杠 + 中间竖笔） ----------
def make_text():
    """上横杠 / 竖笔 / 下横杠 三段矩形；中心对称，竖笔内嵌于横杠"""
    g = blank()
    rect(g, 6, 6, 25, 9, 'X')    # 上横杠
    rect(g, 14, 6, 17, 25, 'X')  # 竖笔（贯穿，与上下横杠相接）
    rect(g, 6, 22, 25, 25, 'X')  # 下横杠
    mask = [[c != '.' for c in row] for row in g]
    return to_matrix(fill_mask(mask, outline_w=1))


# 热点：(16,16) 中心
TEXT = check(make_text())


# ---------- ④ ALIAS：快捷方式（箭头 + 右上角带斜箭头的小方框） ----------
# 12×12 方框：K 描边 + B 填充，内部 W 斜箭头指向东北（↗）
BADGE = [
    'KKKKKKKKKKKK',
    'KBBBBBBWWWWK',
    'KBBBBBBWWBBK',
    'KBBBBBWWBBBK',
    'KBBBBWWBBBBK',
    'KBBBWWBBBBBK',
    'KBBWWBBBBBBK',
    'KBWWBBBBBBBK',
    'KWWBBBBBBBBK',
    'KWBBBBBBBBBK',
    'KBBBBBBBBBBK',
    'KKKKKKKKKKKK',
]


def make_alias():
    """箭头本体 + 右上角方框角标；热点与 ARROW 一致（角标不改变点击原点）"""
    return check(overlay(ARROW, BADGE, 19, 1))


# 热点：(1,1) 与 arrow 一致
ALIAS = make_alias()


# ---------- ⑤ ZOOM_IN / ⑥ ZOOM_OUT：放大镜（左上? 否——镜片右上、手柄左下） ----------
def make_zoom(sign):
    """圆形镜片（K 外圈 + B 内圈 + L 镜片）+ 中心 K 十字(＋)/横线(−) + 左下斜手柄"""
    g = blank()
    cx, cy = 20, 12
    # 手柄（先画，镜片覆盖其根部，形成自然衔接）：左下 45°
    bar(g, 14, 18, 7, 25, 6.0, 'K')
    bar(g, 13.5, 18.5, 7.5, 24.5, 3.0, 'B')
    # 镜片
    disc(g, cx, cy, 6.0, 'L')            # 镜片浅蓝面
    ring(g, cx, cy, 7.5, 6.0, 'B')       # 内圈
    ring(g, cx, cy, 9.0, 7.5, 'K')       # 外圈描边
    # 中心符号（细十字 / 横线）
    bar(g, cx - 3, cy, cx + 3, cy, 2.0, 'K')      # 横线
    if sign == '+':
        bar(g, cx, cy - 3, cx, cy + 3, 2.0, 'K')  # 竖线 → 放大
    return to_matrix(despeckle(g, 1))


# 热点：(6,27) 手柄末端（左下）
ZOOM_IN = check(make_zoom('+'))
ZOOM_OUT = check(make_zoom('-'))


# ---------- ⑦ WAIT：等待沙漏（上下木框 + 收腰玻璃 + 内部沙子） ----------
def make_wait():
    """上盖 / 下盖（K+B）+ 上腔收窄、下腔张开的玻璃（L）+ 颈部与底部沙（M）"""
    g = blank()
    rect(g, 8, 3, 23, 5, 'B')     # 上盖
    rect(g, 8, 26, 23, 28, 'B')   # 下盖
    # 上腔：向下收窄（三角）
    for i, y in enumerate(range(6, 14)):
        half = 8 - i              # 8 → 1
        for x in range(16 - half, 16 + half):
            g[y][x] = 'L'
    # 颈（细，落下中的沙）
    for y in range(14, 18):
        for x in range(15, 17):
            g[y][x] = 'M'
    # 下腔：向下张开（三角）
    for i, y in enumerate(range(18, 26)):
        half = 1 + i              # 1 → 8
        for x in range(16 - half, 16 + half):
            g[y][x] = 'L'
    # 下腔底部沙堆（下半部填 M）
    for y in range(22, 26):
        half = 1 + (y - 18)
        for x in range(16 - half, 16 + half):
            g[y][x] = 'M'
    return to_matrix(outline_chars(g, width=1))


# 热点：(16,16) 中心
WAIT = check(make_wait())


# ---------- ⑧ NOT_ALLOWED：禁止（圆圈描边 + 45° 斜杠） ----------
def make_not_allowed():
    """K 描边圆 + B 填充 + K 斜杠（左上 → 右下，清晰 45°）"""
    g = blank()
    disc(g, 16, 16, 12.5, 'K')
    disc(g, 16, 16, 10.0, 'B')
    bar(g, 8.5, 8.5, 23.5, 23.5, 4.0, 'K')
    return to_matrix(despeckle(g, 2))


# 热点：(16,16) 中心
NOT_ALLOWED = check(make_not_allowed())


# ---------- 造型表：文件名 -> (矩阵, 亮色调色板, 暗色调色板) ----------
# 文件名沿用既有约定，避免改动 assets/css/main.css 里的 --cur-* 变量与选择器：
#   ARROW→arrow  POINTER→hand  TEXT→text  ALIAS→external
#   ZOOM_IN→zoom  ZOOM_OUT→zoom-out  WAIT→wait  NOT_ALLOWED→not-allowed
SHAPES = {
    'arrow':       (ARROW,       'light', 'dark'),
    'hand':        (POINTER,     'light', 'dark'),
    'text':        (TEXT,        'light', 'dark'),
    'external':    (ALIAS,       'light', 'dark'),
    'zoom':        (ZOOM_IN,     'light', 'dark'),
    'zoom-out':    (ZOOM_OUT,    'light', 'dark'),
    'wait':        (WAIT,        'light', 'dark'),
    'not-allowed': (NOT_ALLOWED, 'light', 'dark'),
}


def gen_png(matrix, palette, path):
    """把字符矩阵写成 8bit RGBA PNG（仅 filter 0，最小手写编码）"""
    h, w = len(matrix), len(matrix[0])
    rows = []
    for line in matrix:
        row = bytearray()
        for ch in line:
            if ch == '.':
                row += b'\x00\x00\x00\x00'
            else:
                c = palette[ch]
                r, g, b = c[0], c[1], c[2]
                a = c[3] if len(c) > 3 else 255
                row += bytes((r, g, b, a))
        rows.append(b'\x00' + bytes(row))  # filter 0

    def chunk(t, p):
        return struct.pack('>I', len(p)) + t + p + struct.pack('>I', zlib.crc32(t + p) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
           + chunk(b'IEND', b''))
    path.write_bytes(png)


if __name__ == '__main__':
    for name, (matrix, light_key, dark_key) in SHAPES.items():
        gen_png(matrix, COLORS[light_key], OUT / f'{name}.png')
        gen_png(matrix, COLORS[dark_key], OUT / f'{name}-dark.png')
    print('生成完成:', ', '.join(p.name for p in sorted(OUT.glob('*.png'))))
    print('热点:', ', '.join(f'{k}={v}' for k, v in HOTSPOTS.items()))
