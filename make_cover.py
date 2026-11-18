# -*- coding: utf-8 -*-
"""
Tank Battle - Cardputer ADV  封面 (横版 1280x720)
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, os

W, H = 1280, 720
img = Image.new("RGB", (W, H), (8, 10, 16))
d = ImageDraw.Draw(img)

# ---------------- 背景渐变 ----------------
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(6 + 16 * t), int(10 + 24 * t), int(18 + 36 * t)))

# 战术网格
for x in range(0, W, 52):
    d.line([(x, 0), (x, H)], fill=(18, 32, 40), width=1)
for y in range(0, H, 52):
    d.line([(0, y), (W, y)], fill=(18, 32, 40), width=1)

# 中央光晕
_gr = 260
for _i in range(_gr, 0, -2):
    _t = 1 - _i / _gr
    _a = int(24 * _t * _t)
    d.ellipse([W // 2 - _i, 380 - _i, W // 2 + _i, 380 + _i],
              fill=(10 + _a, 22 + _a, 16 + _a // 2))


# ---------------- 绘制函数 ----------------
def draw_tank(cx, cy, s, body, body2, barrel, facing="up", glow=None):
    if glow:
        d.ellipse([cx - s * 1.4, cy - s * 1.4, cx + s * 1.4, cy + s * 1.4], fill=glow)

    tw_ = s * 0.34
    tl_h = s * 1.0
    d.rounded_rectangle([cx - s, cy - tl_h, cx - s + tw_, cy + tl_h], radius=7, fill=body2)
    d.rounded_rectangle([cx + s - tw_, cy - tl_h, cx + s, cy + tl_h], radius=7, fill=body2)

    n = 8
    for i in range(n):
        yy = cy - tl_h + 6 + i * (2 * tl_h - 12) / (n - 1)
        d.line([(cx - s + 4, yy), (cx - s + tw_ - 4, yy)], fill=(16, 18, 22), width=3)
        d.line([(cx + s - tw_ + 4, yy), (cx + s - 4, yy)], fill=(16, 18, 22), width=3)

    bw = s * 0.62
    d.rounded_rectangle([cx - bw, cy - tl_h, cx + bw, cy + tl_h], radius=9, fill=body)
    d.rounded_rectangle([cx - bw + 4, cy - tl_h + 4, cx - bw + 11, cy + tl_h - 4],
                        radius=4, fill=barrel)

    tr = s * 0.42
    d.ellipse([cx - tr, cy - tr, cx + tr, cy + tr], fill=body, outline=barrel, width=4)
    d.ellipse([cx - tr * 0.55, cy - tr * 0.55, cx + tr * 0.55, cy + tr * 0.55], fill=barrel)

    bl = s * 1.5
    bwid = s * 0.13
    if facing == "up":
        d.rectangle([cx - bwid, cy - bl, cx + bwid, cy - tr * 0.5], fill=barrel)
        d.rectangle([cx - bwid * 1.6, cy - bl - 8, cx + bwid * 1.6, cy - bl + 2], fill=barrel)
    elif facing == "right":
        d.rectangle([cx + tr * 0.5, cy - bwid, cx + bl, cy + bwid], fill=barrel)
        d.rectangle([cx + bl - 2, cy - bwid * 1.6, cx + bl + 8, cy + bwid * 1.6], fill=barrel)
    elif facing == "left":
        d.rectangle([cx - bl, cy - bwid, cx - tr * 0.5, cy + bwid], fill=barrel)
        d.rectangle([cx - bl - 8, cy - bwid * 1.6, cx - bl + 2, cy + bwid * 1.6], fill=barrel)
    else:
        d.rectangle([cx - bwid, cy + tr * 0.5, cx + bwid, cy + bl], fill=barrel)
        d.rectangle([cx - bwid * 1.6, cy + bl - 2, cx + bwid * 1.6, cy + bl + 8], fill=barrel)


def draw_brick(x, y, s, seed=0):
    random.seed(seed)
    base = random.choice([(112, 56, 32), (124, 62, 36), (100, 50, 28)])
    hi = tuple(min(255, c + 42) for c in base)
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=base)
    d.line([(x, y), (x + s - 1, y)], fill=hi, width=2)
    d.line([(x, y + s // 2), (x + s - 1, y + s // 2)], fill=hi, width=2)


def draw_steel(x, y, s):
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=(118, 126, 138))
    d.rectangle([x + 3, y + 3, x + s - 4, y + s - 4], fill=(96, 104, 116))
    d.line([(x + 3, y + 3), (x + s - 4, y + 3)], fill=(190, 198, 210), width=3)
    d.line([(x + 3, y + 3), (x + 3, y + s - 4)], fill=(190, 198, 210), width=3)


# ---------------- 砖墙地形 ----------------
BS = 44
for row in range(2):
    for col in range(10):
        bx = 40 + col * BS
        by = 560 + row * BS
        if by + BS > 700 or bx + BS > 500:
            continue
        draw_brick(bx, by, BS, seed=row * 17 + col)
for k in range(2):
    sx, sy = 40 + 10 * BS, 560 + k * BS
    if sx < 520:
        draw_steel(sx, sy, BS)

# 右侧砖墙
for row in range(2):
    for col in range(6):
        bx = W - 40 - (col + 1) * BS
        by = 560 + row * BS
        if by + BS > 700:
            continue
        draw_brick(bx, by, BS, seed=row * 23 + col + 50)


# ---------------- 双坦克 ----------------
# 绿坦克 P1: 左侧, 朝上
draw_tank(360, 500, 66, (34, 190, 70), (18, 118, 42), (126, 248, 156),
          facing="up", glow=(11, 44, 24))
# 蓝坦克 P2: 右侧, 朝上
draw_tank(890, 500, 66, (40, 130, 220), (22, 74, 140), (146, 206, 255),
          facing="up", glow=(11, 26, 46))


# ---------------- 弹道: 双方朝上, 竖直弹道 ----------------
p1_muzzle_y = 500 - 66 * 1.5
p2_muzzle_y = 500 - 66 * 1.5

# 绿: 竖直向上, 长度控制在副标题下方
for i in range(8):
    t = i / 7
    y = p1_muzzle_y - t * 95
    hw = 7 - i * 0.5
    d.rectangle([360 - hw, y - hw, 360 + hw, y + hw], fill=(150, 255, 180))

# 蓝: 竖直向上
for i in range(8):
    t = i / 7
    y = p2_muzzle_y - t * 95
    hw = 7 - i * 0.5
    d.rectangle([890 - hw, y - hw, 890 + hw, y + hw], fill=(160, 218, 255))

# 火花位置: 弹道顶端, 保持在副标题下方
random.seed(123)
for cx, cy, col_main in [(360, p1_muzzle_y - 108, (160, 255, 190)),
                         (890, p2_muzzle_y - 108, (170, 225, 255))]:
    for i in range(22):
        ang = random.uniform(0, math.tau)
        dist = random.uniform(5, 42)
        x = cx + math.cos(ang) * dist
        y = cy + math.sin(ang) * dist * 0.85
        r = random.uniform(3, 7)
        c = random.choice([(255, 250, 210), (255, 228, 130),
                           col_main, (255, 255, 255)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(255, 255, 240))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))


# ---------------- 字体 ----------------
def font(size):
    for c in ["C:/Windows/Fonts/impact.ttf",
              "C:/Windows/Fonts/ariblk.ttf",
              "C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


f_title = font(142)
f_sub = font(40)
f_small = font(30)
f_badge = font(34)

# ---------------- 标题 ----------------
title = "TANK BATTLE"
tw = d.textlength(title, font=f_title)
tx = (W - tw) / 2
ty = 46

for dx, dy in [(-5, -5), (5, -5), (-5, 5), (5, 5),
               (-7, 0), (7, 0), (0, -7), (0, 9),
               (-3, -3), (3, -3), (-3, 3), (3, 3)]:
    d.text((tx + dx, ty + dy), title, font=f_title, fill=(4, 12, 8))
for i in range(1, 9):
    d.text((tx + i * 0.7, ty + i * 3.0), title, font=f_title, fill=(4, 12, 8))

grad = Image.new("RGB", (int(tw) + 16, 180), (0, 0, 0))
gd = ImageDraw.Draw(grad)
for y in range(180):
    t = y / 180
    gd.line([(0, y), (grad.width, y)],
            fill=(int(126 + 110 * t), int(246 - 46 * t), int(110 + 96 * t)))
mask = Image.new("L", grad.size, 0)
ImageDraw.Draw(mask).text((8, -6), title, font=f_title, fill=255)
img.paste(grad, (int(tx) - 8, int(ty) - 6), mask)
d = ImageDraw.Draw(img)

# ---------------- 副标题 ----------------
sub = "CARDPUTER - ADV"
sw = d.textlength(sub, font=f_sub)
sx = (W - sw) / 2
sy = 206
d.text((sx + 3, sy + 3), sub, font=f_sub, fill=(6, 14, 10))
d.text((sx, sy), sub, font=f_sub, fill=(126, 240, 160))
d.line([(sx, sy + 52), (sx + sw, sy + 52)], fill=(52, 150, 84), width=3)

# ---------------- P1 / VS / P2 徽标 ----------------
# P1 左侧
d.rounded_rectangle([150, 300, 268, 356], radius=12, fill=(14, 52, 28),
                    outline=(60, 210, 110), width=3)
d.text((178, 308), "P1", font=f_badge, fill=(110, 250, 160))

# P2 右侧
d.rounded_rectangle([W - 268, 300, W - 150, 356], radius=12, fill=(14, 30, 58),
                    outline=(70, 170, 245), width=3)
d.text((W - 240, 308), "P2", font=f_badge, fill=(130, 210, 255))

# VS 中间
vs = "VS"
vw = d.textlength(vs, font=f_small)
d.text(((W - vw) / 2, 312), vs, font=f_small, fill=(240, 210, 90))

# ---------------- 底部信息条 ----------------
d.rectangle([0, H - 118, W, H], fill=(6, 12, 10))
d.line([(0, H - 118), (W, H - 118)], fill=(44, 200, 104), width=4)

d.text((60, H - 96), "P1  WASD  +  X", font=f_small, fill=(110, 250, 160))
rx = W - 60 - d.textlength("P2  ARROWS  +  ENTER", font=f_small)
d.text((rx, H - 96), "P2  ARROWS  +  ENTER", font=f_small, fill=(130, 210, 255))

mode_txt = "2P DUEL     /     1P vs AI"
mw = d.textlength(mode_txt, font=f_small)
d.text(((W - mw) / 2, H - 58), mode_txt, font=f_small, fill=(180, 190, 205))

# ---------------- 扫描线 ----------------
overlay = Image.new("RGB", (W, H), (0, 0, 0))
od = ImageDraw.Draw(overlay)
for y in range(0, H, 3):
    od.line([(0, y), (W, y)], fill=(255, 255, 255))
img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img,
                      overlay.convert("L").point(lambda v: 5 if v else 0))

# ---------------- 输出 ----------------
out = r"D:\Administrator\Documents\CardputerAdv_Tank\cover.png"
img.save(out, "PNG")
img.resize((640, 360), Image.LANCZOS).save(
    r"D:\Administrator\Documents\CardputerAdv_Tank\cover_preview.png", "PNG")
print("saved", out, img.size)
