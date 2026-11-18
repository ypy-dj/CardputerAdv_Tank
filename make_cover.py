# -*- coding: utf-8 -*-
"""
Tank Battle - Cardputer ADV  封面 (竖版 540x720)
M5Burner 封面框为竖版比例
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, os

W, H = 540, 720
img = Image.new("RGB", (W, H), (8, 10, 16))
d = ImageDraw.Draw(img)

# ---------------- 背景渐变 ----------------
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=(int(6 + 16 * t), int(10 + 24 * t), int(18 + 36 * t)))

# 战术网格
for x in range(0, W, 36):
    d.line([(x, 0), (x, H)], fill=(18, 32, 40), width=1)
for y in range(0, H, 36):
    d.line([(0, y), (W, y)], fill=(18, 32, 40), width=1)

# 中央光晕
_gr = 170
for _i in range(_gr, 0, -2):
    _t = 1 - _i / _gr
    _a = int(24 * _t * _t)
    d.ellipse([W // 2 - _i, 400 - _i, W // 2 + _i, 400 + _i],
              fill=(10 + _a, 22 + _a, 16 + _a // 2))


# ---------------- 绘制函数 ----------------
def draw_tank(cx, cy, s, body, body2, barrel, facing="up", glow=None):
    if glow:
        d.ellipse([cx - s * 1.4, cy - s * 1.4, cx + s * 1.4, cy + s * 1.4], fill=glow)

    tw_ = s * 0.34
    tl_h = s * 1.0
    d.rounded_rectangle([cx - s, cy - tl_h, cx - s + tw_, cy + tl_h], radius=6, fill=body2)
    d.rounded_rectangle([cx + s - tw_, cy - tl_h, cx + s, cy + tl_h], radius=6, fill=body2)

    n = 7
    for i in range(n):
        yy = cy - tl_h + 5 + i * (2 * tl_h - 10) / (n - 1)
        d.line([(cx - s + 3, yy), (cx - s + tw_ - 3, yy)], fill=(16, 18, 22), width=2)
        d.line([(cx + s - tw_ + 3, yy), (cx + s - 3, yy)], fill=(16, 18, 22), width=2)

    bw = s * 0.62
    d.rounded_rectangle([cx - bw, cy - tl_h, cx + bw, cy + tl_h], radius=8, fill=body)
    d.rounded_rectangle([cx - bw + 3, cy - tl_h + 3, cx - bw + 9, cy + tl_h - 3],
                        radius=3, fill=barrel)

    tr = s * 0.42
    d.ellipse([cx - tr, cy - tr, cx + tr, cy + tr], fill=body, outline=barrel, width=3)
    d.ellipse([cx - tr * 0.55, cy - tr * 0.55, cx + tr * 0.55, cy + tr * 0.55], fill=barrel)

    bl = s * 1.45
    bwid = s * 0.13
    if facing == "up":
        d.rectangle([cx - bwid, cy - bl, cx + bwid, cy - tr * 0.5], fill=barrel)
        d.rectangle([cx - bwid * 1.5, cy - bl - 6, cx + bwid * 1.5, cy - bl + 2], fill=barrel)
    elif facing == "right":
        d.rectangle([cx + tr * 0.5, cy - bwid, cx + bl, cy + bwid], fill=barrel)
        d.rectangle([cx + bl - 2, cy - bwid * 1.5, cx + bl + 6, cy + bwid * 1.5], fill=barrel)
    elif facing == "left":
        d.rectangle([cx - bl, cy - bwid, cx - tr * 0.5, cy + bwid], fill=barrel)
        d.rectangle([cx - bl - 6, cy - bwid * 1.5, cx - bl + 2, cy + bwid * 1.5], fill=barrel)
    else:
        d.rectangle([cx - bwid, cy + tr * 0.5, cx + bwid, cy + bl], fill=barrel)
        d.rectangle([cx - bwid * 1.5, cy + bl - 2, cx + bwid * 1.5, cy + bl + 6], fill=barrel)


def draw_brick(x, y, s, seed=0):
    random.seed(seed)
    base = random.choice([(112, 56, 32), (124, 62, 36), (100, 50, 28)])
    hi = tuple(min(255, c + 42) for c in base)
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=base)
    d.line([(x, y), (x + s - 1, y)], fill=hi, width=2)
    d.line([(x, y + s // 2), (x + s - 1, y + s // 2)], fill=hi, width=1)


def draw_steel(x, y, s):
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=(118, 126, 138))
    d.rectangle([x + 2, y + 2, x + s - 3, y + s - 3], fill=(96, 104, 116))
    d.line([(x + 2, y + 2), (x + s - 3, y + 2)], fill=(190, 198, 210), width=2)
    d.line([(x + 2, y + 2), (x + 2, y + s - 3)], fill=(190, 198, 210), width=2)


# ---------------- 砖墙 ----------------
BS = 26
for row in range(2):
    for col in range(7):
        bx = 28 + col * BS
        by = 596 + row * BS
        if by + BS > 700:
            continue
        draw_brick(bx, by, BS, seed=row * 11 + col)
for k in range(2):
    sx, sy = 28 + 7 * BS, 596 + k * BS
    if sx < W - 30:
        draw_steel(sx, sy, BS)


# ---------------- 双坦克 ----------------
# 绿坦克 P1: 右上, 朝左
draw_tank(340, 390, 50, (34, 190, 70), (18, 118, 42), (126, 248, 156),
          facing="left", glow=(11, 44, 24))
# 蓝坦克 P2: 左下, 朝上
draw_tank(185, 495, 50, (40, 130, 220), (22, 74, 140), (146, 206, 255),
          facing="up", glow=(11, 26, 46))


# ---------------- 弹道(各自沿炮管方向) ----------------
# 绿坦克 (340,390) 朝左: 炮口在左侧
muzzle_green = (340 - 50 * 1.45, 390)
# 蓝坦克 (185,495) 朝上: 炮口在上方
muzzle_blue = (185, 495 - 50 * 1.45)

# 两条弹道在 (260, 390) 交汇: 绿朝左x递减, 蓝朝上y递减
hit_x = muzzle_green[0] - 40
hit_y = muzzle_blue[1] + 40

# 绿: 水平向左 - 方形子弹颗粒
for i in range(7):
    t = i / 6
    x = muzzle_green[0] + (hit_x - muzzle_green[0]) * t
    hw = 4.5 - i * 0.35
    d.rectangle([x - hw, muzzle_green[1] - hw, x + hw, muzzle_green[1] + hw],
                fill=(150, 255, 180))

# 蓝: 竖直向上 - 方形子弹颗粒
for i in range(7):
    t = i / 6
    y = muzzle_blue[1] + (hit_y - muzzle_blue[1]) * t
    hw = 4.5 - i * 0.35
    d.rectangle([muzzle_blue[0] - hw, y - hw, muzzle_blue[0] + hw, y + hw],
                fill=(160, 218, 255))

hx, hy = hit_x, hit_y
random.seed(77)
for i in range(26):
    ang = random.uniform(0, math.tau)
    dist = random.uniform(5, 40)
    x = hx + math.cos(ang) * dist
    y = hy + math.sin(ang) * dist
    r = random.uniform(2, 6)
    col = random.choice([(255, 250, 210), (255, 228, 130),
                         (200, 245, 255), (255, 255, 255)])
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=(255, 255, 240))
d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=(255, 255, 255))


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


f_title = font(74)
f_sub = font(22)
f_small = font(18)

# ---------------- 标题 ----------------
title = "TANK BATTLE"
tw = d.textlength(title, font=f_title)
tx = (W - tw) / 2
ty = 40

for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3),
               (-4, 0), (4, 0), (0, -4), (0, 5),
               (-2, -2), (2, -2), (-2, 2), (2, 2)]:
    d.text((tx + dx, ty + dy), title, font=f_title, fill=(4, 12, 8))
for i in range(1, 6):
    d.text((tx + i * 0.5, ty + i * 2.0), title, font=f_title, fill=(4, 12, 8))

grad = Image.new("RGB", (int(tw) + 10, 96), (0, 0, 0))
gd = ImageDraw.Draw(grad)
for y in range(96):
    t = y / 96
    gd.line([(0, y), (grad.width, y)],
            fill=(int(126 + 110 * t), int(246 - 46 * t), int(110 + 96 * t)))
mask = Image.new("L", grad.size, 0)
ImageDraw.Draw(mask).text((5, -2), title, font=f_title, fill=255)
img.paste(grad, (int(tx) - 5, int(ty) - 2), mask)
d = ImageDraw.Draw(img)

# ---------------- 副标题 ----------------
sub = "CARDPUTER - ADV"
sw = d.textlength(sub, font=f_sub)
sx = (W - sw) / 2
sy = 128
d.text((sx + 2, sy + 2), sub, font=f_sub, fill=(6, 14, 10))
d.text((sx, sy), sub, font=f_sub, fill=(126, 240, 160))
d.line([(sx, sy + 30), (sx + sw, sy + 30)], fill=(52, 150, 84), width=2)

# ---------------- P1 / VS / P2 ----------------
d.rounded_rectangle([58, 186, 138, 218], radius=7, fill=(14, 52, 28),
                    outline=(60, 210, 110), width=2)
d.text((76, 191), "P1", font=f_small, fill=(110, 250, 160))

d.rounded_rectangle([W - 138, 186, W - 58, 218], radius=7, fill=(14, 30, 58),
                    outline=(70, 170, 245), width=2)
d.text((W - 120, 191), "P2", font=f_small, fill=(130, 210, 255))

vs = "VS"
vw = d.textlength(vs, font=f_small)
d.text(((W - vw) / 2, 190), vs, font=f_small, fill=(240, 210, 90))

# ---------------- 底部信息条 ----------------
d.rectangle([0, H - 96, W, H], fill=(6, 12, 10))
d.line([(0, H - 96), (W, H - 96)], fill=(44, 200, 104), width=3)

d.text((26, H - 82), "P1  WASD  +  X", font=f_small, fill=(110, 250, 160))
rx = W - 26 - d.textlength("P2  ARROWS  +  ENTER", font=f_small)
d.text((rx, H - 82), "P2  ARROWS  +  ENTER", font=f_small, fill=(130, 210, 255))

mode_txt = "2P DUEL   /   1P vs AI"
mw = d.textlength(mode_txt, font=f_small)
d.text(((W - mw) / 2, H - 54), mode_txt, font=f_small, fill=(180, 190, 205))

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
img.resize((405, 540), Image.LANCZOS).save(
    r"D:\Administrator\Documents\CardputerAdv_Tank\cover_preview.png", "PNG")
print("saved", out, img.size)
