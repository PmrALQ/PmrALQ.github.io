# -*- coding: utf-8 -*-
"""
箭头造型探索脚本（仅用于设计比选，不参与站点构建）

用途：
  1. 用多边形离屏光栅化出多组候选箭头轮廓，打印 24x24 像素矩阵便于精确比对；
  2. 输出一张多比例尺对照图（1x / 2x / 6x，亮底 / 暗底），用于肉眼判断实际显示效果。

依赖：仅标准库（zlib + struct 手写 PNG）。
"""
import struct
import zlib
import pathlib
import sys

W = H = 24

# ---------------------------------------------------------------- PNG IO


def write_png(path, w, h, rows):
    """rows: 每行是 [(r,g,b[,a]), ...]，统一补足为 RGBA 后写出 PNG-32"""
    raw = bytearray()
    for r in rows:
        raw.append(0)
        for px in r:
            raw += bytes(px) if len(px) == 4 else bytes((px[0], px[1], px[2], 255))
    assert len(raw) == h * (w * 4 + 1), '像素数据长度与 IHDR 声明不符: %d' % len(raw)

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

    hdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', hdr) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    pathlib.Path(path).write_bytes(png)
    return path


def read_png(path):
    d = pathlib.Path(path).read_bytes()
    pos, w, h, idat = 8, None, None, b''
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        data = d[pos + 8:pos + 8 + ln]
        if typ == b'IHDR':
            w, h = struct.unpack('>II', data[:8])
        elif typ == b'IDAT':
            idat += data
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 4
    out, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - 4] if i >= 4 else 0
            b = prev[i]
            c = prev[i - 4] if i >= 4 else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        prev = line
        out.append([tuple(line[x * 4:x * 4 + 4]) for x in range(w)])
    return w, h, out


# ---------------------------------------------------------------- 光栅化


def rasterize(verts, w=W, h=H):
    """把多边形光栅化成 inside / outline 两个布尔矩阵（像素中心在 x+0.5, y+0.5）"""
    inside = [[False] * w for _ in range(h)]
    n = len(verts)
    for y in range(h):
        cy = y + 0.5
        xs = []
        for i in range(n):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % n]
            if (y1 <= cy) != (y2 <= cy):
                t = (cy - y1) / float(y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            a, b = xs[k], xs[k + 1]
            for x in range(w):
                if a <= x + 0.5 <= b:
                    inside[y][x] = True

    outline = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if not inside[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or not inside[ny][nx]:
                    outline[y][x] = True
                    break
    return inside, outline


def paint(inside, outline, fill, line, key=None, w=W, h=H):
    """按 inside / outline 上色；key（可选）为填色与描边之间的 1px 亮色分隔线"""
    rows = [[(0, 0, 0, 0)] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if not inside[y][x]:
                continue
            rows[y][x] = line if outline[y][x] else fill
    if key is not None:
        # 取「填充像素中与描边相邻」的那一圈，换成 key 色
        for y in range(h):
            for x in range(w):
                if not inside[y][x] or outline[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and outline[ny][nx]:
                        rows[y][x] = key
                        break
    return rows


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


# ---------------------------------------------------------------- 矩阵打印

LEGEND = {
    'line': 'K',
    'fill': 'B',
    'key': 'W',
}


def show(name, rows, fmt):
    print('=== %s ===' % name)
    for y in range(H):
        line = ''
        for x in range(W):
            px = rows[y][x]
            if px[3] < 40:
                line += '.'
            else:
                line += fmt(px)
        print('%2d %s' % (y, line))
    print()


# ---------------------------------------------------------------- 对照图合成


def blit(dst, dw, dh, src, sx, sy, scale, bg):
    """把 src（任意尺寸）按最近邻放大 scale 倍后合成到 dst 的 (sx, sy)；透明像素落到 bg 上"""
    sh = len(src)
    sw = len(src[0]) if sh else 0
    for y in range(sh):
        for x in range(sw):
            px = src[y][x]
            if px[3] < 8:
                c = bg
            else:
                al = px[3] / 255.0
                c = tuple(int(px[i] * al + bg[i] * (1 - al)) for i in range(3))
            for dy in range(scale):
                for dx in range(scale):
                    px2, py2 = sx + x * scale + dx, sy + y * scale + dy
                    if 0 <= px2 < dw and 0 <= py2 < dh:
                        dst[py2][px2] = c


def build_sheet(cands, out_path, cols=2):
    """每个候选占一格：上排 [6x亮底][6x暗底]，下排 [2x亮底][2x暗底][1x亮底][1x暗底]"""
    sc_big = 6
    pad = 16
    tile = W * sc_big
    cell_w = tile * 2 + 10
    cell_h = tile + 60
    rows_n = (len(cands) + cols - 1) // cols
    dw = pad + cols * (cell_w + pad)
    dh = pad + rows_n * (cell_h + pad)
    page = [[(255, 255, 255)] * dw for _ in range(dh)]

    light = (245, 245, 247)
    dark = (29, 29, 31)

    for i, (label, rows) in enumerate(cands):
        r, c = divmod(i, cols)
        x0 = pad + c * (cell_w + pad)
        y0 = pad + r * (cell_h + pad)
        blit(page, dw, dh, rows, x0, y0, sc_big, light)
        blit(page, dw, dh, rows, x0 + tile + 10, y0, sc_big, dark)
        y1 = y0 + tile + 10
        blit(page, dw, dh, rows, x0, y1, 2, light)
        blit(page, dw, dh, rows, x0 + 54, y1, 2, dark)
        blit(page, dw, dh, rows, x0 + 108, y1, 1, light)
        blit(page, dw, dh, rows, x0 + 138, y1, 1, dark)

    write_png(out_path, dw, dh, page)
    return out_path, dw, dh


# ---------------------------------------------------------------- 候选轮廓

# 直尾：tip=(tx,ty)，头部直角边长 L，尾宽 Wt（左右边缘均垂直），尾高 Ht
def cursor_poly(tx, ty, L, Wt, Ht):
    return [
        (tx, ty),                                # 尖端
        (tx + L, ty + L),                        # 右翼尖（斜边严格 45°）
        (tx + Wt, ty + L),                       # 沿头部下缘左行至尾右上
        (tx + Wt, ty + L + Ht),                  # 尾右下
        (tx, ty + L + Ht),                       # 尾左下
        (tx, ty + L),                            # 头部左下 = 尾左上
    ]


# 收尾：左缘保持垂直（与头部左缘共线），右缘向内收，形成锥形尾
def taper_poly(tx, ty, L, top_r, bot_r, Ht):
    return [
        (tx, ty),
        (tx + L, ty + L),
        (tx + top_r, ty + L),
        (tx + bot_r, ty + L + Ht),
        (tx, ty + L + Ht),
        (tx, ty + L),
    ]


CANDS = [
    ('legacy(当前)', 'PNG:public/cursors/arrow.png'),
    ('A 直尾 W4 H8', cursor_poly(2, 1, 11, 4, 8)),
    ('B 直尾 W5 H8', cursor_poly(2, 1, 11, 5, 8)),
    ('C 收尾 8>5', taper_poly(2, 1, 11, 7, 4, 9)),
    ('D 收尾 7>4', taper_poly(2, 1, 11, 6, 3, 9)),
    ('E 短头 L10', cursor_poly(2, 1, 10, 5, 9)),
]

# 几何定案：尖端 (2,1)，头部直角边 11，尾自 y=12 至 y=21、右缘 9 行内收 3px，左缘与头部左缘共线
CHOSEN = taper_poly(2, 1, 11, 7, 4, 9)

# (标签, 亮色(填充,描边,分隔线), 暗色(填充,描边,分隔线))
PALETTES = [
    ('P1 现行·深蓝描边', ('#378ADD', '#0C447C', None), ('#55A0EB', '#EBF2FA', None)),
    ('P2 中蓝描边',      ('#4A9BE9', '#1D5FA8', None), ('#6FB6F2', '#0E3358', None)),
    ('P3 浅蓝描边',      ('#5AAAF0', '#2F7AC8', None), ('#86C6F7', '#0E3358', None)),
    ('P4 实心·无描边',   ('#3D8FE0', None, None),      ('#6FB6F2', None, None)),
    ('P5 白分隔三明治',  ('#378ADD', '#0C447C', '#FFFFFF'), ('#6FB6F2', '#08121F', None)),
]


def make_rows(verts, pal):
    fill = hexc(pal[0])
    line = hexc(pal[1]) if pal[1] else fill
    key = hexc(pal[2]) if pal[2] else None
    inside, outline = rasterize(verts)
    return paint(inside, outline, fill, line, key)


def build_palette_sheet(entries, out_path):
    """每行一种配色：左 6x 亮底、右 6x 暗底，下方 2x / 1x 实际尺寸参考"""
    sc = 6
    pad = 16
    tile = W * sc
    cell_w = tile * 2 + 10
    cell_h = tile + 60
    dw = pad * 2 + cell_w
    dh = pad + len(entries) * (cell_h + pad)
    page = [[(255, 255, 255)] * dw for _ in range(dh)]

    light = (245, 245, 247)
    dark = (29, 29, 31)

    for i, (label, lp, dp) in enumerate(entries):
        x0 = pad
        y0 = pad + i * (cell_h + pad)
        rl = make_rows(CHOSEN, lp)
        rd = make_rows(CHOSEN, dp)
        blit(page, dw, dh, rl, x0, y0, sc, light)
        blit(page, dw, dh, rd, x0 + tile + 10, y0, sc, dark)
        y1 = y0 + tile + 10
        blit(page, dw, dh, rl, x0, y1, 2, light)
        blit(page, dw, dh, rd, x0 + 54, y1, 2, dark)
        blit(page, dw, dh, rl, x0 + 108, y1, 1, light)
        blit(page, dw, dh, rd, x0 + 138, y1, 1, dark)

    write_png(out_path, dw, dh, page)
    return out_path, dw, dh

PALETTE = {
    'line': hexc('#0C447C'),
    'fill': hexc('#378ADD'),
    'key': hexc('#FFFFFF'),
}


def main():
    out_dir = pathlib.Path('project-report/board')
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered = []
    for label, spec in CANDS:
        if isinstance(spec, str) and spec.startswith('PNG:'):
            _, w, h, rows = (None, *read_png(spec[4:]))
            rendered.append((label, rows))
            continue
        inside, outline = rasterize(spec)
        rows = paint(inside, outline, PALETTE['fill'], PALETTE['line'])
        rendered.append((label, rows))
        show(label, rows, lambda px: 'K' if px[:3] == PALETTE['line'][:3] else 'B')

    p, dw, dh = build_sheet(rendered, out_dir / 'arrow-probe.png')
    print('造型对照图: %s  %dx%d' % (p, dw, dh))

    p2, dw2, dh2 = build_palette_sheet(PALETTES, out_dir / 'arrow-palette.png')
    print('配色对照图: %s  %dx%d' % (p2, dw2, dh2))


if __name__ == '__main__':
    main()
