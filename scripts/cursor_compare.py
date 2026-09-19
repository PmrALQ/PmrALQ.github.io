# -*- coding: utf-8 -*-
"""
光标全族前后对照图（仅用于设计评审，不参与站点构建）

输出 project-report/board/cursor-compare.png：
  每个光标一格，从左到右依次为 [v1 亮色][v2 亮色][v1 暗色][v2 暗色]，5 倍最近邻放大。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cursor_arrow_probe import read_png, write_png, blit, W  # noqa: E402

NAMES = ['arrow', 'hand', 'text', 'external', 'zoom', 'zoom-out', 'wait', 'not-allowed']
V1_DIR = pathlib.Path('project-report/board/v1')
V2_DIR = pathlib.Path('public/cursors')
OUT = pathlib.Path('project-report/board/cursor-compare.png')

LIGHT = (245, 245, 247)
DARK = (29, 29, 31)


def load(p):
    _, _w, _h, rows = (None, *read_png(p))
    return rows


def main():
    sc = 5
    pad = 16
    gap = 8
    tile = W * sc
    cell_w = tile * 4 + gap * 3
    cell_h = tile + gap
    cols, rows_n = 2, 4

    dw = pad + cols * (cell_w + pad)
    dh = pad + rows_n * (cell_h + pad)
    page = [[(255, 255, 255)] * dw for _ in range(dh)]

    for i, name in enumerate(NAMES):
        r, c = divmod(i, cols)
        x0 = pad + c * (cell_w + pad)
        y0 = pad + r * (cell_h + pad)
        v1 = load(V1_DIR / f'{name}.png')
        v2 = load(V2_DIR / f'{name}.png')
        for k, (img, bg) in enumerate(((v1, LIGHT), (v2, LIGHT), (v1, DARK), (v2, DARK))):
            blit(page, dw, dh, img, x0 + k * (tile + gap), y0, sc, bg)
        # 每格底部画一条基线，分隔相邻光标
        for xx in range(dw):
            page[y0 + cell_h + 4][xx] = (228, 228, 233)

    write_png(OUT, dw, dh, page)
    print('前后对照图: %s  %dx%d' % (OUT, dw, dh))


if __name__ == '__main__':
    main()
