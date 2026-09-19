"""把 public/cursors/ 的实际素材拼成一张对照图, 供人工确认造型与热点
- 直接读 project-report/real-*.png (由 preview_cursor.py 放大 10 倍)
- 每个光标下方标注名称, 并在热点位置画红色十字准星
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRE = ROOT / 'project-report'
OUT = PRE / 'cursor-sheet-v3.png'

# 8 个光标: (文件名, 中文名, 热点x, 热点y)
ITEMS = [
    ('arrow',      '默认箭头',   1, 1),
    ('hand',       '手型指针',   5, 2),
    ('text',       '文本 I 型',  16, 16),
    ('external',   '外链快捷',   1, 1),
    ('zoom',       '放大镜 +',   6, 27),
    ('zoom-out',   '放大镜 −',   6, 27),
    ('wait',       '等待沙漏',   16, 16),
    ('not-allowed', '禁止',      16, 16),
]

SCALE = 10          # preview_cursor.py 的放大倍数
CELL_W, CELL_H = 340, 380
COLS = 4
PAD = 20
HEADER = 54

FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
try:
    f_title = ImageFont.truetype(FONT_PATH, 26)
    f_cell = ImageFont.truetype(FONT_PATH, 20)
    f_note = ImageFont.truetype(FONT_PATH, 17)
except Exception:
    f_title = f_cell = f_note = ImageFont.load_default()

LIGHT_BG = (247, 248, 250)
DARK_BG = (17, 19, 23)


def build_section(imgs, title, dark):
    """一个区块: 4 列 x 2 行"""
    rows = (len(imgs) + COLS - 1) // COLS
    w = PAD * 2 + COLS * CELL_W
    h = HEADER + rows * CELL_H + PAD
    canvas = Image.new('RGB', (w, h), LIGHT_BG if not dark else DARK_BG)
    d = ImageDraw.Draw(canvas)
    d.text((PAD, 14), title, font=f_title, fill=(20, 24, 32) if not dark else (235, 240, 248))

    for i, (img, name, hx, hy) in enumerate(imgs):
        cx = PAD + (i % COLS) * CELL_W
        cy = HEADER + (i // COLS) * CELL_H
        # 卡片底
        card = (255, 255, 255) if not dark else (32, 36, 43)
        d.rounded_rectangle([cx, cy, cx + CELL_W - 14, cy + CELL_H - 14], 10, fill=card)
        # 光标图
        if img:
            canvas.paste(img, (cx + (CELL_W - 14 - img.width) // 2, cy + 10), img)
            # 热点准星
            ox = cx + (CELL_W - 14 - img.width) // 2
            oy = cy + 10
            px, py = ox + hx * SCALE, oy + hy * SCALE
            r = 11
            d.ellipse([px - r, py - r, px + r, py + r], outline=(217, 45, 32), width=3)
            d.line([px - r - 6, py, px + r + 6, py], fill=(217, 45, 32), width=2)
            d.line([px, py - r - 6, px, py + r + 6], fill=(217, 45, 32), width=2)
        # 名称 + 热点坐标
        label = f'{name}'
        d.text((cx + 14, cy + CELL_H - 62), label, font=f_cell,
               fill=(20, 24, 32) if not dark else (232, 238, 246))
        d.text((cx + 14, cy + CELL_H - 34), f'热点 {hx},{hy}', font=f_note,
               fill=(120, 128, 140) if not dark else (150, 158, 170))
    return canvas


def load(name, suffix):
    p = PRE / f'real-{name}{suffix}.png'
    return Image.open(p).convert('RGBA') if p.exists() else None


light = [(load(n, ''), label, hx, hy) for n, label, hx, hy in ITEMS]
dark = [(load(n, '-dark'), label, hx, hy) for n, label, hx, hy in ITEMS]

s1 = build_section(light, '亮色主题（Light）', False)
s2 = build_section(dark, '夜间主题（Dark）', True)

W = s1.width
gap = 8
final = Image.new('RGB', (W, s1.height + gap + s2.height), (128, 132, 140))
final.paste(s1, (0, 0))
final.paste(s2, (0, s1.height + gap))
final.save(OUT)
print('已生成:', OUT, final.size)
