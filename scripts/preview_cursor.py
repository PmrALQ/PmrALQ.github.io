"""从实际生成的指针 PNG 里解码并放大, 产出预览图 (用于确认文件真实长相)
纯标准库: 反向解析本项目 gen_cursors.py 写出的 PNG (filter 0 + RGBA)

v3 · 2026-09-16 工具改进：
  - 默认模式改为遍历 public/cursors/ 下**全部** png（不再写死 4 个 / 8 个文件名），
    新增光标无需再改脚本；
  - 调色板同步到 v3 的 5 色（K/B/M/L/W），svg/combine 两版预览尺寸改为按 PNG 实际尺寸自适应。
"""
import struct
import zlib
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / 'public' / 'cursors'
DST = Path(__file__).resolve().parent.parent / 'project-report'
DST.mkdir(exist_ok=True)


def decode_png(path):
    """解码本项目写出的 PNG, 返回 (w, h, [[(r,g,b,a), ...], ...])"""
    data = Path(path).read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', '不是 PNG'
    pos = 8
    w = h = None
    idat = b''
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b'IHDR':
            w, h, bd, ct = struct.unpack('>IIBB', body[:10])
            assert bd == 8 and ct == 6, f'只支持 8bit RGBA, 实际 bd={bd} ct={ct}'
        elif tag == b'IDAT':
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 4
    rows = []
    for y in range(h):
        off = y * (stride + 1)
        assert raw[off] == 0, '仅支持 filter 0'
        line = raw[off + 1:off + 1 + stride]
        rows.append([tuple(line[x * 4:x * 4 + 4]) for x in range(w)])
    return w, h, rows


def write_png(path, pixels, w, h):
    def chunk(tag, d):
        c = tag + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
    raw = b''
    for y in range(h):
        raw += b'\x00'
        for x in range(w):
            raw += bytes(pixels[y * w + x])
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    Path(path).write_bytes(png)


def upscale(rows, w, h, scale, bg):
    """放大到 scale 倍, 透明像素填充 bg (让透明区域可见)"""
    out = []
    for y in range(h):
        for _ in range(scale):
            for x in range(w):
                r, g, b, a = rows[y][x]
                if a == 0:
                    px = bg
                else:
                    px = (r, g, b, 255)
                for _ in range(scale):
                    out.append(px)
    return out


def combine(name, path, scale=12,
            bg_light=(255, 255, 255, 255), bg_dark=(17, 19, 24, 255)):
    """把同一套光标的亮/暗两版并排合成一张 (尺寸按 PNG 实际大小自适应)"""
    w1, h1, rows1 = decode_png(SRC / f'{name}.png')
    w2, h2, rows2 = decode_png(SRC / f'{name}-dark.png')
    big1 = upscale(rows1, w1, h1, scale, bg_light)
    big2 = upscale(rows2, w2, h2, scale, bg_dark)
    lw = w1 * scale
    W = lw + w2 * scale
    H = max(h1, h2) * scale
    out = []
    for y in range(H):
        for x in range(W):
            if x < lw:
                out.append(big1[y * lw + x] if y < h1 * scale else bg_light)
            else:
                xx = x - lw
                out.append(big2[y * w2 * scale + xx] if y < h2 * scale else bg_dark)
    write_png(path, out, W, H)
    print(f'combine -> {path.name}  {W}x{H}')


# ── 设计规范画板：把光标转成矢量像素路径（画布上等比放大不失真） ──
# v3 调色板（与 gen_cursors.py 的 COLORS 保持一致）
CSS_LIGHT = {'K': '#0C1A5E', 'B': '#1E96F0', 'M': '#63C6F8', 'L': '#B3E2FD', 'W': '#FFFFFF'}
CSS_DARK = {'K': '#F2F7FF', 'B': '#4FAEF5', 'M': '#9BD8FB', 'L': '#D6EEFE', 'W': '#FFFFFF'}

# 名称 -> (亮色调色板, 暗色调色板)
BOARD_THEMES = {
    'arrow': (CSS_LIGHT, CSS_DARK),
    'hand': (CSS_LIGHT, CSS_DARK),
    'text': (CSS_LIGHT, CSS_DARK),
    'external': (CSS_LIGHT, CSS_DARK),
    'zoom': (CSS_LIGHT, CSS_DARK),
    'zoom-out': (CSS_LIGHT, CSS_DARK),
    'wait': (CSS_LIGHT, CSS_DARK),
    'not-allowed': (CSS_LIGHT, CSS_DARK),
}


def rects_path(rows, target, ox=0):
    """贪心矩形分解：把同色像素压成尽量大的矩形，输出 SVG path 的 d 字符串
    ox: 整体 x 方向偏移（把亮/暗两版直接烘进同一坐标系，避免用 transform）"""
    h = len(rows)
    w = max(len(r) for r in rows)
    filled = [[x < len(rows[y]) and rows[y][x] == target for x in range(w)] for y in range(h)]
    d = []
    for y in range(h):
        for x in range(w):
            if not filled[y][x]:
                continue
            rw = 1
            while x + rw < w and filled[y][x + rw]:
                rw += 1
            rh = 1
            while y + rh < h and all(filled[y + rh][x + k] for k in range(rw)):
                rh += 1
            for yy in range(y, y + rh):
                for xx in range(x, x + rw):
                    filled[yy][xx] = False
            d.append(f'M{x + ox} {y}h{rw}v{rh}h-{rw}z')
    return ''.join(d)


def _to_chars(rows, pal):
    """RGBA 行 → 字符矩阵（按该主题调色板反查 K/B/M/L/W）"""
    rev = {}
    for k, hexv in pal.items():
        rev[(int(hexv[1:3], 16), int(hexv[3:5], 16), int(hexv[5:7], 16))] = k
    return [''.join('.' if p[3] < 128 else rev.get((p[0], p[1], p[2]), '?')
                    for p in row) for row in rows]


def cursor_svg_inline(name, scale=5.5):
    """单个光标 → 亮/暗并排的自包含 SVG。
    不使用 <defs>/<use>/transform（部分 SVG 解析器不支持），
    两版路径坐标直接烘焙，只保留扁平 <rect>/<path> 元素。"""
    w1, h1, r1 = decode_png(SRC / f'{name}.png')
    w2, h2, r2 = decode_png(SRC / f'{name}-dark.png')
    pal_l, pal_d = BOARD_THEMES[name]
    m1, m2 = _to_chars(r1, pal_l), _to_chars(r2, pal_d)

    W = w1 * scale * 2
    H = h1 * scale
    parts = [f'<svg width="{W:g}" height="{H:g}" viewBox="0 0 {w1 * 2} {h1}" '
             f'xmlns="http://www.w3.org/2000/svg">',
             f'<rect x="0" y="0" width="{w1}" height="{h1}" fill="#FFFFFF"/>',
             f'<rect x="{w1}" y="0" width="{w1}" height="{h1}" fill="#111318"/>']
    for k in sorted(set(pal_l) | set(pal_d)):
        dl = rects_path(m1, k)
        dd = rects_path(m2, k, ox=w1)
        if dl:
            parts.append(f'<path d="{dl}" fill="{pal_l[k]}"/>')
        if dd:
            parts.append(f'<path d="{dd}" fill="{pal_d[k]}"/>')
    parts.append('</svg>')
    return ''.join(parts)


def cursor_svg(name, scale=5.5):
    """单个光标 → 亮/暗并排的 SVG（<defs>+<use> 复用路径，体积减半）"""
    w1, h1, r1 = decode_png(SRC / f'{name}.png')
    w2, h2, r2 = decode_png(SRC / f'{name}-dark.png')
    pal_l, pal_d = BOARD_THEMES[name]

    m1, m2 = _to_chars(r1, pal_l), _to_chars(r2, pal_d)
    keys = sorted(set(pal_l) | set(pal_d))
    W = w1 * scale * 2
    H = h1 * scale
    out = [f'<svg width="{W:g}" height="{H:g}" viewBox="0 0 {w1 * 2} {h1}" '
           f'xmlns="http://www.w3.org/2000/svg">',
           f'<rect x="0" y="0" width="{w1}" height="{h1}" fill="#FFFFFF"/>',
           f'<rect x="{w1}" y="0" width="{w1}" height="{h1}" fill="#111318"/>']
    defs, uses = [], []
    for k in keys:
        dl = rects_path(m1, k)
        dd = rects_path(m2, k)
        if dl:
            defs.append(f'<path id="{name}{k}" d="{dl}"/>')
            uses.append(f'<use href="#{name}{k}" fill="{pal_l[k]}"/>')
        if dd:
            if dd == dl:
                # 亮/暗两版形状完全一致时复用同一路径，只换填充与位移
                uses.append(f'<use href="#{name}{k}" fill="{pal_d[k]}" '
                            f'transform="translate({w1} 0)"/>')
            else:
                defs.append(f'<path id="{name}{k}d" d="{dd}"/>')
                uses.append(f'<use href="#{name}{k}d" fill="{pal_d[k]}" '
                            f'transform="translate({w1} 0)"/>')
    out.append('<defs>' + ''.join(defs) + '</defs>')
    out += uses
    out.append('</svg>')
    return ''.join(out)


NAMES = ['arrow', 'hand', 'text', 'external', 'zoom', 'zoom-out', 'wait', 'not-allowed']


if __name__ == '__main__':
    import sys as _sys
    mode = _sys.argv[1] if len(_sys.argv) > 1 else 'preview'

    if mode == 'combine':
        board = DST / 'board'
        board.mkdir(exist_ok=True)
        for n in NAMES:
            combine(n, board / f'cursor-{n}.png')
        raise SystemExit(0)

    if mode == 'svg':
        board = DST / 'board'
        board.mkdir(exist_ok=True)
        out = board / 'cursors.svg.txt'
        with out.open('w', encoding='utf-8') as f:
            for n in NAMES:
                f.write(f'### {n}\n{cursor_svg(n)}\n')
        print('svg ->', out, out.stat().st_size, 'B')
        raise SystemExit(0)

    if mode == 'inline':
        board = DST / 'board'
        board.mkdir(exist_ok=True)
        out = board / 'cursors.inline.svg.txt'
        with out.open('w', encoding='utf-8') as f:
            for n in NAMES:
                f.write(f'### {n}\n{cursor_svg_inline(n)}\n')
        print('inline ->', out, out.stat().st_size, 'B')
        raise SystemExit(0)

    # 默认模式：遍历 public/cursors/ 下全部 png（含 -dark），逐张放大预览
    scale = 10
    files = sorted(SRC.glob('*.png'))
    if not files:
        print(f'未找到任何 png: {SRC}')
        raise SystemExit(1)
    for f in files:
        bg = (17, 19, 23, 255) if f.stem.endswith('-dark') else (245, 246, 248, 255)
        w, h, rows = decode_png(f)
        px = upscale(rows, w, h, scale, bg)
        out = DST / f'real-{f.stem}.png'
        write_png(out, px, w * scale, h * scale)
        print(f'{f.name}  {w}x{h}  ->  {out.name}  {w * scale}x{h * scale}')
