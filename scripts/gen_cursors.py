"""
生成像素风蓝色鼠标光标（PNG）：
  - arrow.png / arrow-dark.png   像素箭头（默认状态）
  - hand.png / hand-dark.png     像素手（悬停交互元素）
亮色版黑描边 + 亮蓝填充；暗色版白描边 + 亮蓝填充。
热点：箭头 (1,1)，手 (2,1)。
"""
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'public' / 'cursors'
OUT.mkdir(exist_ok=True)

# 像素箭头 24×24（K=描边 B=填充 .=透明）——经典 8-bit 箭头 + 三脚尾巴
ARROW = [
    'KBBB.................',
    'K.B.B................',
    'K..B.B...............',
    'K...B.B..............',
    'K....B.B.............',
    'K.....B.B............',
    'K......B.B...........',
    'K.......B.B..........',
    'K........B.B.........',
    'K.........B.B........',
    'K..........B.B.......',
    'K...........B.B......',
    'K............B.B.....',
    'K.............B.B....',
    'K..............B.B...',
    'K...............B.B..',
    'K................B.B.',
    'K.................B.B',
    'K..................B.',
    'K..................B.',
    'KBB.BB.BB.............',
    'K..B.B..B.............',
    '.B.B.B..B.............',
    '..B.B...B.............',
]

# 像素手 24×24（指尖朝左上）——简化竖掌
HAND = [
    '...KBBB...............',
    '..KBBBBBB.............',
    '..KBBBBBB.............',
    '..KBBBBBB.............',
    '..KBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    'KBBBBBBBB.............',
    'KBBBBBBBB.............',
    'KBBBBBBBB.............',
    'KBBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '.KBBBBBBB.............',
    '..KBBBBB..............',
    '..KBBBBB..............',
    '..KBBBBB..............',
    '..KBBBBB..............',
    '...KBBB...............',
    '...KBBB...............',
]

COLORS = {
    'light': {'K': (13, 24, 33), 'B': (64, 196, 255)},    # 深色描边 + 亮水蓝
    'dark':  {'K': (255, 255, 255), 'B': (125, 216, 255)}, # 白色描边 + 亮水蓝
}


def gen_png(matrix, palette, path):
    h, w = len(matrix), len(matrix[0])
    rows = []
    for line in matrix:
        row = bytearray()
        for ch in line:
            if ch == '.':
                row += b'\x00\x00\x00\x00'
            else:
                r, g, b = palette[ch]
                row += bytes((r, g, b, 255))
        rows.append(b'\x00' + bytes(row))  # filter 0

    def chunk(t, p):
        return struct.pack('>I', len(p)) + t + p + struct.pack('>I', zlib.crc32(t + p) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(b''.join(rows), 9))
           + chunk(b'IEND', b''))
    path.write_bytes(png)


for mode, palette in COLORS.items():
    suffix = '' if mode == 'light' else '-dark'
    gen_png(ARROW, palette, OUT / f'arrow{suffix}.png')
    gen_png(HAND, palette, OUT / f'hand{suffix}.png')

print('生成完成:', ', '.join(p.name for p in sorted(OUT.glob('*.png'))))
