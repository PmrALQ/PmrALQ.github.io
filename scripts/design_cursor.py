"""像素风蓝色鼠标指针生成器
- 同一套像素数据 (grid) 驱动两种产物:
  1) 放大预览 SVG(粘贴到 show_widget 给用户挑选)
  2) 透明背景 PNG(写入 public/cursors/, 供 CSS cursor: url() 使用)
纯标准库生成 PNG(手写 PNG 编码), 无第三方依赖。
"""
import struct
import zlib
import sys
import os

# ---------- 调色板 ----------
PALETTE = {
    'o': (12, 68, 124, 255),      # 深海军蓝 描边 (c-blue 800)
    'b': (24, 95, 165, 255),      # 主蓝     (c-blue 600)
    'l': (133, 183, 235, 255),    # 亮蓝 高光 (c-blue 200)
    'w': (255, 255, 255, 255),    # 白 滚轮/反光
    'k': (8, 40, 80, 255),        # 最深 描边补深
    '.': (0, 0, 0, 0),            # 透明
}

# ---------- 方案 A: 蓝色像素箭头 (经典指针造型) ----------
GRID_A = [
    'b................',
    'bb...............',
    'b.b..............',
    'bwb..............',
    'b.bb.............',
    'b..bb............',
    'b..wbb...........',
    'b....bb..........',
    'b....wbb.........',
    'b......bb........',
    'b......wbb.......',
    'b........bb......',
    'b........bb......',
    'bbbbbbbbbbbbbb...',
    '.bbbbbbbbbbbb....',
    '..b.b.b.b.b......',
    '...b.b.b.b.......',
]

# ---------- 方案 B: 蓝色像素鼠标(外设造型, 含滚轮) ----------
GRID_B = [
    '.....ooooo......',
    '...oobbbbboo....',
    '..obbbbbbbbbo...',
    '.obbbbbbbbbbbo..',
    '.obwbllbbwbwbo..',
    '.obwblbbwbwbbo..',
    '.obwbbbllbwbbo..',
    '.obwbbbbbbwboo..',
    '.obbbbbbbbbbo...',
    '..obbbbbbbbbo...',
    '...oobbbbbbo....',
    '.....ooooo......',
    '.......b........',
    '.......b........',
]

def grid_size(grid):
    return max(len(r) for r in grid), len(grid)

def cell_at(grid, x, y):
    if y < 0 or y >= len(grid):
        return '.'
    row = grid[y]
    if x < 0 or x >= len(row):
        return '.'
    return row[x]

# ---------- PNG 编码 (最小实现) ----------
def write_png(path, pixels, width, height):
    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))
    raw = b''
    for y in range(height):
        raw += b'\x00'  # filter type 0
        for x in range(width):
            raw += bytes(pixels[y * width + x])
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)

def make_png(grid, scale, path):
    w, h = grid_size(grid)
    pixels = []
    for gy in range(h):
        for gx in range(w):
            c = PALETTE[cell_at(grid, gx, gy)]
            for _ in range(scale):
                pixels.append(c)
        # scale 倍纵向复制
        for _ in range(scale - 1):
            for gx in range(w):
                for _ in range(scale):
                    pixels.append(PALETTE[cell_at(grid, gx, gy)])
    write_png(path, pixels, w * scale, h * scale)

# ---------- SVG 预览 (供 show_widget) ----------
def preview_svg(grid, title, hot_x, hot_y, scale=24, img_path=''):
    w, h = grid_size(grid)
    W = w * scale
    H = h * scale
    s = []
    s.append(f'<svg viewBox="0 0 680 {H + 110}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img">')
    s.append(f'<title>{title}</title>')
    ox = (680 - W) // 2
    s.append(f'<image href="{img_path}" x="{ox}" y="8" width="{W}" height="{H}" style="image-rendering:pixelated"/>')
    s.append(f'<circle cx="{ox + hot_x * scale + scale / 2}" cy="{8 + hot_y * scale + scale / 2}" r="9" fill="none" stroke="#d92d20" stroke-width="3"/>')
    s.append(f'<text x="{ox}" y="{H + 46}" font-family="system-ui,sans-serif" font-size="18" font-weight="500" fill="var(--color-text-primary)">{title}</text>')
    s.append(f'<text x="{ox}" y="{H + 72}" font-family="system-ui,sans-serif" font-size="14" fill="var(--color-text-secondary)">红圈 = 点击热点 (悬停/点击的判定点)</text>')
    s.append(f'</svg>')
    return ''.join(s)

def grid_hot(grid, x, y):
    return x, y

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'svg'
    if mode == 'png':
        # 32px = 2x 16px 网格; 输出给 CSS 用
        os.makedirs('public/cursors', exist_ok=True)
        make_png(GRID_A, 2, 'public/cursors/arrow-blue.png')
        make_png(GRID_B, 2, 'public/cursors/mouse-blue.png')
        print('已生成 public/cursors/arrow-blue.png (32x32)')
        print('已生成 public/cursors/mouse-blue.png (32x32)')
    elif mode == 'preview':
        # 放大预览 PNG + 内联 SVG, 供 show_widget 展示给用户挑选
        os.makedirs('project-report', exist_ok=True)
        make_png(GRID_A, 24, 'project-report/preview-a.png')
        make_png(GRID_B, 24, 'project-report/preview-b.png')
        a = preview_svg(GRID_A, '方案 A · 蓝色像素箭头(经典指针)', 0, 0, 24, 'project-report/preview-a.png')
        b = preview_svg(GRID_B, '方案 B · 蓝色像素鼠标(外设造型)', 6, 0, 24, 'project-report/preview-b.png')
        with open('project-report/svg_a.txt', 'w', encoding='utf-8') as f:
            f.write(a)
        with open('project-report/svg_b.txt', 'w', encoding='utf-8') as f:
            f.write(b)
        print('SVG A chars:', len(a), '| SVG B chars:', len(b))
    else:
        print('usage: design_cursor.py [png|preview]')
