# -*- coding: utf-8 -*-
"""
Tank Battle - Cardputer ADV  封面
720x720 (M5Burner 封面规格)
双人对战主题: 绿坦克 vs 蓝坦克
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, os

W = H = 720
img = Image.new("RGB", (W, H), (8, 10, 16))
d = ImageDraw.Draw(img)

# ---------------- 背景渐变 ----------------
for y in range(H):
    t = y / H
    r = int(6 + 16 * t)
    g = int(10 + 22 * t)
    b = int(18 + 34 * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# 战术网格
for x in range(0, W, 45):
    d.line([(x, 0), (x, H)], fill=(18, 32, 40), width=1)
for y in range(0, H, 45):
    d.line([(0, y), (W, y)], fill=(18, 32, 40), width=1)

# 中央暖色光晕（小而柔和，只衬托子弹交汇点）
_glow_r = 110
for _i in range(_glow_r, 0, -2):
    _t = 1 - _i / _glow_r
    _a = int(22 * _t * _t)
    d.ellipse([315 - _i, 250 - _i, 315 + _i, 250 + _i],
              fill=(10 + _a, 22 + _a, 16 + _a // 2))


# ---------------- 绘制函数 ----------------
def draw_tank(d, cx, cy, s, body, body2, barrel, facing="up", glow=None):
    """绘制坦克 (俯视)"""
    if glow:
        d.ellipse([cx - s * 1.5, cy - s * 1.5, cx + s * 1.5, cy + s * 1.5], fill=glow)

    # 履带
    tw_ = s * 0.34
    tl_h = s * 1.0
    d.rounded_rectangle([cx - s, cy - tl_h, cx - s + tw_, cy + tl_h], radius=6, fill=body2)
    d.rounded_rectangle([cx + s - tw_, cy - tl_h, cx + s, cy + tl_h], radius=6, fill=body2)

    # 履带纹
    n = 7
    for i in range(n):
        yy = cy - tl_h + 5 + i * (2 * tl_h - 10) / (n - 1)
        d.line([(cx - s + 3, yy), (cx - s + tw_ - 3, yy)], fill=(16, 18, 22), width=2)
        d.line([(cx + s - tw_ + 3, yy), (cx + s - 3, yy)], fill=(16, 18, 22), width=2)

    # 车体
    bw = s * 0.62
    d.rounded_rectangle([cx - bw, cy - tl_h, cx + bw, cy + tl_h], radius=8, fill=body)
    # 车体高光
    d.rounded_rectangle([cx - bw + 3, cy - tl_h + 3, cx - bw + 9, cy + tl_h - 3],
                        radius=3, fill=barrel)

    # 炮塔
    tr = s * 0.42
    d.ellipse([cx - tr, cy - tr, cx + tr, cy + tr], fill=body, outline=barrel, width=3)
    d.ellipse([cx - tr * 0.55, cy - tr * 0.55, cx + tr * 0.55, cy + tr * 0.55],
              fill=barrel)

    # 炮管
    bl = s * 1.5
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
    else:  # down
        d.rectangle([cx - bwid, cy + tr * 0.5, cx + bwid, cy + bl], fill=barrel)
        d.rectangle([cx - bwid * 1.5, cy + bl - 2, cx + bwid * 1.5, cy + bl + 6], fill=barrel)


def draw_brick(d, x, y, s, seed=0):
    random.seed(seed)
    base = random.choice([(112, 56, 32), (124, 62, 36), (100, 50, 28)])
    hi = tuple(min(255, c + 42) for c in base)
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=base)
    d.line([(x, y), (x + s - 1, y)], fill=hi, width=2)
    d.line([(x, y + s // 2), (x + s - 1, y + s // 2)], fill=hi, width=1)


def draw_steel(d, x, y, s):
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=(118, 126, 138))
    d.rectangle([x + 2, y + 2, x + s - 3, y + s - 3], fill=(96, 104, 116))
    d.line([(x + 2, y + 2), (x + s - 3, y + 2)], fill=(190, 198, 210), width=2)
    d.line([(x + 2, y + 2), (x + 2, y + s - 3)], fill=(190, 198, 210), width=2)


# ---------------- 地面砖墙 ----------------
BS = 28
for row in range(3):
    for col in range(8):
        bx = 30 + col * BS
        by = 548 + row * BS
        if by + BS > 686:
            continue
        draw_brick(d, bx, by, BS, seed=row * 13 + col)

# 钢墙点缀
for k in range(2):
    sx = 30 + 8 * BS
    sy = 548 + k * BS
    if sx < W - 40:
        draw_steel(d, sx, sy, BS)


# ---------------- 双坦克 ----------------
# 绿坦克 (P1) 左下, 朝上
draw_tank(d, 215, 430, 58, (34, 190, 70), (18, 118, 42), (126, 248, 156),
          facing="up", glow=(11, 44, 24))

# 蓝坦克 (P2) 右上, 朝左
draw_tank(d, 510, 268, 58, (40, 130, 220), (22, 74, 140), (146, 206, 255),
          facing="left", glow=(11, 26, 46))


# ---------------- 弹道（沿炮管方向，符合物理） ----------------
# 绿坦克朝上: 子弹从炮口竖直向上飞
muzzle_p1 = (215, 430 - 58 * 1.5)
# 蓝坦克朝左: 子弹从炮口水平向左飞
muzzle_p2 = (510 - 58 * 1.5, 268)

# 两条弹道在 (215, 268) 附近相交 —— 各自按炮管方向直线延伸
# P1: x=215 固定, y 从 muzzle_p1[1] 递减
# P2: y=268 固定, x 从 muzzle_p2[0] 递减
# 取相遇点为 P1 竖直线上 y=268 那点
hit_x = 215
hit_y = 268

for i in range(13):
    t = i / 12
    y = muzzle_p1[1] + (hit_y - muzzle_p1[1]) * t
    rr = 6 - i * 0.35
    d.ellipse([hit_x - rr, y - rr, hit_x + rr, y + rr], fill=(255, 238, 124))

for i in range(13):
    t = i / 12
    x = muzzle_p2[0] + (hit_x - muzzle_p2[0]) * t
    rr = 6 - i * 0.35
    d.ellipse([x - rr, hit_y - rr, x + rr, hit_y + rr], fill=(136, 218, 255))

mid = (hit_x, hit_y)

# 中央碰撞火花
hx, hy = mid
random.seed(99)
for i in range(30):
    ang = random.uniform(0, math.tau)
    dist = random.uniform(6, 52)
    x = hx + math.cos(ang) * dist
    y = hy + math.sin(ang) * dist
    r = random.uniform(2.5, 7)
    col = random.choice([(255, 250, 200), (255, 220, 120),
                         (200, 240, 255), (255, 255, 255)])
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)
d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=(255, 255, 235))
d.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=(255, 255, 255))


# ---------------- 字体 ----------------
def font(size):
    cands = ["C:/Windows/Fonts/impact.ttf",
             "C:/Windows/Fonts/ariblk.ttf",
             "C:/Windows/Fonts/arialbd.ttf",
             "C:/Windows/Fonts/arial.ttf"]
    for c in cands:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


f_title = font(96)
f_sub = font(26)
f_small = font(21)

# ---------------- 标题 ----------------
title = "TANK BATTLE"
tw = d.textlength(title, font=f_title)
tx = (W - tw) / 2
ty = 44

# 黑色描边 + 投影
for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3),
               (-4, 0), (4, 0), (0, -4), (0, 6),
               (-2, -2), (2, -2), (-2, 2), (2, 2)]:
    d.text((tx + dx, ty + dy), title, font=f_title, fill=(4, 12, 8))
# 底部投影
for i in range(1, 7):
    d.text((tx + i * 0.6, ty + i * 2.2), title, font=f_title, fill=(4, 12, 8))

# 渐变填充
grad = Image.new("RGB", (int(tw) + 12, 120), (0, 0, 0))
gd = ImageDraw.Draw(grad)
for y in range(120):
    t = y / 120
    gd.line([(0, y), (grad.width, y)],
            fill=(int(126 + 110 * t), int(246 - 46 * t), int(110 + 96 * t)))
mask = Image.new("L", grad.size, 0)
ImageDraw.Draw(mask).text((6, -4), title, font=f_title, fill=255)
img.paste(grad, (int(tx) - 6, int(ty) - 4), mask)
d = ImageDraw.Draw(img)

# ---------------- 副标题 ----------------
sub = "CARDPUTER - ADV"
sw = d.textlength(sub, font=f_sub)
sx = (W - sw) / 2
sy = 152
d.text((sx + 2, sy + 2), sub, font=f_sub, fill=(6, 14, 10))
d.text((sx, sy), sub, font=f_sub, fill=(126, 240, 160))
d.line([(sx, sy + 34), (sx + sw, sy + 34)], fill=(52, 150, 84), width=2)

# ---------------- 双人标识 ----------------
# 左: P1 绿色徽标
d.rounded_rectangle([36, 214, 120, 250], radius=8, fill=(14, 52, 28),
                    outline=(60, 210, 110), width=2)
d.text((48, 220), "P1", font=f_small, fill=(110, 250, 160))

# 右: P2 蓝色徽标
d.rounded_rectangle([W - 120, 214, W - 36, 250], radius=8, fill=(14, 30, 58),
                    outline=(70, 170, 245), width=2)
d.text((W - 106, 220), "P2", font=f_small, fill=(130, 210, 255))

# 中间 VS
vs = "VS"
vw = d.textlength(vs, font=f_small)
d.text(((W - vw) / 2, 218), vs, font=f_small, fill=(240, 210, 90))

# ---------------- 操作提示条 ----------------
d.rectangle([0, H - 88, W, H], fill=(6, 12, 10))
d.line([(0, H - 88), (W, H - 88)], fill=(44, 200, 104), width=3)

# 操作说明
lines = [
    ("P1: WASD + X", (110, 250, 155)),
    ("P2: ARROWS + ENTER", (130, 210, 255)),
]
# 两列
d.text((40, H - 74), "P1  WASD  +  X", font=f_small, fill=(110, 250, 160))
rx = W - 40 - d.textlength("P2  ARROWS  +  ENTER", font=f_small)
d.text((rx, H - 74), "P2  ARROWS  +  ENTER", font=f_small, fill=(130, 210, 255))
d.text(((W - d.textlength("2P DUEL  /  1P vs AI", font=f_small)) / 2, H - 44),
       "2P DUEL  /  1P vs AI", font=f_small, fill=(180, 190, 205))

# ---------------- 扫描线 ----------------
overlay = Image.new("RGB", (W, H), (0, 0, 0))
od = ImageDraw.Draw(overlay)
for y in range(0, H, 3):
    od.line([(0, y), (W, y)], fill=(255, 255, 255))
mask_scan = overlay.convert("L").point(lambda v: 5 if v else 0)
img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img, mask_scan)

# ---------------- 输出 ----------------
out = r"D:\Administrator\Documents\CardputerAdv_Tank\cover.png"
img.save(out, "PNG")
img.resize((480, 480), Image.LANCZOS).save(
    r"D:\Administrator\Documents\CardputerAdv_Tank\cover_preview.png", "PNG")
print("saved", out, img.size)
