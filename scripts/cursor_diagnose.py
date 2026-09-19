"""诊断 + 对照图: 检查白晕残留, 并拼出亮/暗背景对照图"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / 'public' / 'cursors'
PRE = ROOT / 'project-report' / 'extract'
SHEET = ROOT / 'project-report' / 'extract' / 'cursor-sheet-extracted.png'

NAMES = ['arrow', 'hand', 'text', 'external', 'zoom', 'zoom-out', 'wait', 'not-allowed']
LABELS = {'arrow': '默认箭头', 'hand': '手型指针', 'text': '文本 I 型', 'external': '外链快捷',
          'zoom': '放大镜 +', 'zoom-out': '放大镜 −', 'wait': '等待沙漏', 'not-allowed': '禁止'}
HOT = {'arrow': (5, 0), 'hand': (11, 0), 'text': (19, 19), 'external': (3, 5),
       'zoom': (3, 39), 'zoom-out': (3, 39), 'wait': (19, 19), 'not-allowed': (19, 19)}

print('=== 诊断: 每个光标文件 ===')
ok = True
for n in NAMES:
    p = CUR / f'{n}.png'
    im = Image.open(p)
    a = np.asarray(im.convert('RGBA')).astype(np.int32)
    opaque = a[:, :, 3] > 0
    lum = a[:, :, :3].sum(axis=2)
    whiteish = opaque & (lum > 690)
    colors = len(set(map(tuple, a[opaque][:, :3].tolist())))
    flag = ''
    if im.size != (40, 40) or im.mode != 'RGBA':
        flag = '  <== 尺寸/模式异常'; ok = False
    print(f'  {n:12s} {im.size} {im.mode}  不透明={opaque.sum():>4}px  其中近白={whiteish.sum():>4}px'
          f'  色数={colors}{flag}')
    if whiteish.sum() > opaque.sum() * 0.45:
        print('        ^ 近白占比偏高, 可能仍有白晕')

print('\nok' if ok else '\n有问题')

# ---- 对照图 ----
SCALE = 5
CELL = 40 * SCALE
PAD = 18
HEAD = 46

try:
    f_title = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 24)
    f_cell = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 18)
except Exception:
    f_title = f_cell = ImageFont.load_default()


def section(bg, title, text_color, card, suffix=''):
    cols = 4
    rows = 2
    w = PAD * 2 + cols * (CELL + PAD)
    h = HEAD + rows * (CELL + 46)
    cv = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(cv)
    d.text((PAD, 10), title, font=f_title, fill=text_color)
    for i, n in enumerate(NAMES):
        cx = PAD + (i % cols) * (CELL + PAD)
        cy = HEAD + (i // cols) * (CELL + 46)
        d.rounded_rectangle([cx - 6, cy - 6, cx + CELL + 6, cy + CELL + 6], 8, fill=card)
        im = Image.open(CUR / f'{n}{suffix}.png').convert('RGBA')
        big = im.resize((CELL, CELL), Image.NEAREST)
        cv.paste(big, (cx, cy), big)
        hx, hy = HOT[n]
        px, py = cx + hx * SCALE, cy + hy * SCALE
        r = 9
        d.ellipse([px - r, py - r, px + r, py + r], outline=(217, 45, 32), width=2)
        d.line([px - 16, py, px + 16, py], fill=(217, 45, 32), width=1)
        d.line([px, py - 16, px, py + 16], fill=(217, 45, 32), width=1)
        d.text((cx, cy + CELL + 8), f'{LABELS[n]}  {hx},{hy}', font=f_cell, fill=text_color)
    return cv


s1 = section((247, 248, 250), '日间套 · 参考图原色(蓝)', (20, 24, 32), (255, 255, 255), '')
s2 = section((17, 19, 23), '夜间套 · 青色(对齐 --accent #00FFFF)', (232, 238, 246), (30, 34, 41), '-dark')
final = Image.new('RGB', (s1.width, s1.height + 8 + s2.height), (120, 124, 132))
final.paste(s1, (0, 0))
final.paste(s2, (0, s1.height + 8))
final.save(SHEET)
print('对照图:', SHEET, final.size)
