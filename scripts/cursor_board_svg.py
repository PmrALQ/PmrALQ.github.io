# -*- coding: utf-8 -*-
"""
为 Ardot 画板生成矢量面板 SVG（仅用于设计评审，不参与站点构建）

为什么不用位图：本机 http_proxy 会改写 COS 预签名请求导致上传 403，
因此画板上的光标一律用「矢量重绘」——按像素矩形分解成 <path>，
坐标在 Python 侧直接烘焙（不使用 <defs> / <use> / transform，规避画板 SVG 解析器的兼容风险），
放大到任意倍数都不失真。

输出 project-report/board/svg2/*.svg
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cursor_arrow_probe import read_png  # noqa: E402

N = 24
V1 = pathlib.Path('project-report/board/v1')
V2 = pathlib.Path('public/cursors')
OUT = pathlib.Path('project-report/board/svg2')

LIGHT = '#F5F5F7'
DARK = '#1D1D1F'


def rects(mask, x0, y0, s):
    """贪心矩形分解：把同色像素压成尽量大的矩形，输出 path 的 d 字符串"""
    h, w = len(mask), len(mask[0])
    filled = [row[:] for row in mask]
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
            d.append('M%d %dh%dv%dh-%dz' % (x0 + x * s, y0 + y * s, rw * s, rh * s, rw * s))
    return ''.join(d)


def load(path):
    _n, _w, _h, rows = (None, *read_png(path))
    return rows


def svg_cursor(rows, x0, y0, s, bg=None):
    """把一个 24×24 光标渲染成若干 <path>（按颜色分组，忽略全透明像素）"""
    groups = {}
    for y in range(N):
        for x in range(N):
            r, g, b, a = rows[y][x]
            if a == 0:
                continue
            groups.setdefault((r, g, b, a), []).append((x, y))

    out = []
    if bg:
        out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x0, y0, N * s, N * s, bg))
    # 先画面积大的（填充），再画面积小的（描边 / 高光），保证覆盖关系正确
    for (r, g, b, a), pix in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        mask = [[False] * N for _ in range(N)]
        for px, py in pix:
            mask[py][px] = True
        op = '' if a == 255 else ' fill-opacity="%.2f"' % (a / 255.0)
        out.append('<path d="%s" fill="#%02X%02X%02X"%s/>' % (rects(mask, x0, y0, s), r, g, b, op))
    return ''.join(out)


def wrap(w, h, body):
    return ('<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">%s</svg>'
            % (w, h, w, h, body))


def grid_path(x0, y0, s, n=N, color='#DCE3EA'):
    """1px 像素栅格：用描边路径表达，比逐条 rect 省一个数量级"""
    d = []
    for i in range(n + 1):
        d.append('M%d %dv%d' % (x0 + i * s, y0, n * s))
        d.append('M%d %dh%d' % (x0, y0 + i * s, n * s))
    return '<path d="%s" fill="none" stroke="%s" stroke-width="1"/>' % (''.join(d), color)


def write(name, svg):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    p.write_text(svg, encoding='utf-8')
    print('%-22s %6d B' % (name, p.stat().st_size))


# ── 面板 1：v2 定案几何（8× + 像素栅格）
def panel_geom():
    s, pad = 8, 10
    v = load(V2 / 'arrow.png')
    body = ('<rect x="%d" y="%d" width="%d" height="%d" fill="#FFFFFF"/>' % (pad, pad, N * s, N * s)
            + grid_path(pad, pad, s)
            + svg_cursor(v, pad, pad, s))
    write('geom-v2.svg', wrap(N * s + pad * 2, N * s + pad * 2, body))


# ── 面板 2/3：前后对照（v1 | v2，同底色，6×）。亮暗分开，控制单文件体积
def panel_ab(suffix, bg):
    s, gap = 6, 8
    v1 = load((V1 if suffix == 'light' else V1) / ('arrow.png' if suffix == 'light' else 'arrow-dark.png'))
    v2 = load((V2) / ('arrow.png' if suffix == 'light' else 'arrow-dark.png'))
    body = svg_cursor(v1, 0, 0, s, bg) + svg_cursor(v2, N * s + gap, 0, s, bg)
    write('ab-%s.svg' % suffix, wrap(2 * N * s + gap, N * s, body))


# ── 面板 4/5：造型比选（亮底 5×，按 3+2 拆分）
CAND_POLYS = {
    'A': [(2, 1), (13, 12), (6, 12), (6, 20), (2, 20), (2, 12)],   # 直尾 W4
    'B': [(2, 1), (13, 12), (7, 12), (7, 20), (2, 20), (2, 12)],   # 直尾 W5
    'C': [(2, 1), (13, 12), (9, 12), (6, 21), (2, 21), (2, 12)],   # 收尾 8>5（定案）
    'D': [(2, 1), (13, 12), (8, 12), (5, 21), (2, 21), (2, 12)],   # 收尾 7>4
    'E': [(2, 1), (12, 11), (7, 11), (7, 20), (2, 20), (2, 11)],   # 短头 L10
}

LINE_RGB = (31, 99, 174, 255)
FILL_RGB = (64, 147, 228, 255)


def _candidate_rows(key):
    from gen_cursors import raster, outline_of  # noqa: E402
    inside = raster(CAND_POLYS[key])
    outline = outline_of(inside)
    rows = [[(0, 0, 0, 0)] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            if inside[y][x]:
                rows[y][x] = LINE_RGB if outline[y][x] else FILL_RGB
    return rows


def panel_shapes(name, keys):
    s, gap = 5, 10
    body = ''
    x = 0
    for k in keys:
        body += svg_cursor(_candidate_rows(k), x, 0, s, LIGHT)
        x += N * s + gap
    write(name, wrap(x - gap, N * s, body))


if __name__ == '__main__':
    panel_geom()
    panel_ab('light', LIGHT)
    panel_ab('dark', DARK)
    panel_shapes('shapes-abc.svg', ['A', 'B', 'C'])
    panel_shapes('shapes-de.svg', ['D', 'E'])
