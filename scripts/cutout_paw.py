"""
抠图脚本：白底浅蓝猫爪 → 透明背景 RGBA PNG（白底色度键 + 边缘柔化 + 缩放到 320px）
一次性工具，处理 猫爪.png → public/images/paw.png
"""
import struct
import zlib
from pathlib import Path

# 源图在项目根目录（用户放置），输出到 public/images/paw.png
SRC = Path(__file__).resolve().parent.parent / '猫爪.png'
DST = Path(__file__).resolve().parent.parent / 'public' / 'images' / 'paw.png'
OUT_SIZE = 320

# ── 1. 读取并解压 ──────────────────────────────────────────────
data = SRC.read_bytes()
w, h = struct.unpack('>II', data[16:24])
bit_depth, color_type = data[24], data[25]
assert bit_depth == 8 and color_type == 2, f'需要 8bit RGB PNG，实际 {bit_depth}/{color_type}'

idat = b''
pos = 8
while pos < len(data):
    length = struct.unpack('>I', data[pos:pos + 4])[0]
    ctype = data[pos + 4:pos + 8]
    if ctype == b'IDAT':
        idat += data[pos + 8:pos + 8 + length]
    pos += 12 + length
raw = zlib.decompress(idat)

# ── 2. unfilter 还原每行 ───────────────────────────────────────
stride = w * 3
rows = []
prev = bytearray(stride)

def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c

for y in range(h):
    off = y * (stride + 1)
    ft = raw[off]
    row = bytearray(raw[off + 1:off + 1 + stride])
    if ft == 1:
        for i in range(3, stride):
            row[i] = (row[i] + row[i - 3]) & 0xFF
    elif ft == 2:
        for i in range(stride):
            row[i] = (row[i] + prev[i]) & 0xFF
    elif ft == 3:
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            row[i] = (row[i] + ((left + prev[i]) >> 1)) & 0xFF
    elif ft == 4:
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            up = prev[i]
            ul = prev[i - 3] if i >= 3 else 0
            row[i] = (row[i] + paeth(left, up, ul)) & 0xFF
    rows.append(bytes(row))
    prev = row

# ── 3. 双线性缩放到 OUT_SIZE ───────────────────────────────────
def sample(x, y):
    """双线性采样 RGB（x,y 为源图浮点坐标）"""
    x = max(0.0, min(w - 1.0001, x))
    y = max(0.0, min(h - 1.0001, y))
    x0, y0 = int(x), int(y)
    dx, dy = x - x0, y - y0
    r0 = rows[y0]
    r1 = rows[y0 + 1] if y0 + 1 < h else r0
    out = bytearray(3)
    for c in range(3):
        p00 = r0[x0 * 3 + c]
        p10 = r0[x0 * 3 + 3 + c] if x0 + 1 < w else p00
        p01 = r1[x0 * 3 + c]
        p11 = r1[x0 * 3 + 3 + c] if x0 + 1 < w else p01
        top = p00 + (p10 - p00) * dx
        bot = p01 + (p11 - p01) * dx
        out[c] = round(top + (bot - top) * dy)
    return out

# ── 4. 白底色度键：白底 → 透明，主体保留，边缘柔化 ────────────
def alpha_of(r, g, b):
    # min(r,g,b) 越接近 255 越白；主体是浅蓝(约 164,219,250)等彩色
    m = min(r, g, b)
    a = round((240 - m) * 3.6)   # m≥240 全透明；m≤170 全不透明；中间渐变
    return 0 if a < 0 else 255 if a > 255 else a

out_rows = []
for y in range(OUT_SIZE):
    sy = (y + 0.5) * h / OUT_SIZE
    row = bytearray()
    for x in range(OUT_SIZE):
        sx = (x + 0.5) * w / OUT_SIZE
        r, g, b = sample(sx, sy)
        row += bytes((r, g, b, alpha_of(r, g, b)))
    out_rows.append(bytes(row))

# ── 5. 编码 PNG（RGBA, 8bit）────────────────────────────────────
def chunk(ctype, payload):
    return struct.pack('>I', len(payload)) + ctype + payload + struct.pack('>I', zlib.crc32(ctype + payload) & 0xFFFFFFFF)

ihdr = struct.pack('>IIBBBBB', OUT_SIZE, OUT_SIZE, 8, 6, 0, 0, 0)
idat_payload = zlib.compress(b''.join(b'\x00' + r for r in out_rows), 9)
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', ihdr)
       + chunk(b'IDAT', idat_payload)
       + chunk(b'IEND', b''))

DST.write_bytes(png)
print(f'完成: {SRC} ({w}x{h}) → {DST} ({OUT_SIZE}x{OUT_SIZE}, {len(png)/1024:.0f}KB)')
