import sys; sys.path.insert(0, '/home/claude/work')
import render_v2 as R
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
R.init()
W, H = 1920, 1080
def bg():
    fr = R.BG.copy() if R.BG.mode == 'RGBA' else R.BG.convert('RGBA')
    fr.alpha_composite(R.GLOW); return fr
def sprite(name, idx, h, glow=None, flip=False):
    big, fx, fy, mk, im = R.ANIM[name][idx]
    spr = R.apply_glow(big, mk, glow, 10.0) if glow else big
    s = h / spr.height
    out = spr.resize((int(spr.width * s), int(spr.height * s)), Image.LANCZOS)
    if flip: out = out.transpose(Image.FLIP_LEFT_RIGHT)
    return out
def put(fr, im, cx, bottom):
    fr.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))
def txt(t, size, col=(255, 255, 255), stroke=8, glow=0, f=R.F_RUSSO):
    return R.text_img(t, R.font(f, size), col + (255,), stroke=stroke, stroke_fill=(0, 0, 0), glow=glow, glowcol=R.RED)
def pill(fr, im, cx, cy, fill=R.RED, pad=(36, 14)):
    d = ImageDraw.Draw(fr)
    w, h = im.width + pad[0] * 2, im.height + pad[1] * 2
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 26, fill=fill + (255,), outline=(255, 255, 255, 255), width=5)
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def shadow(fr, cx, y, w):
    sh = Image.new('RGBA', (w + 120, 200), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([60, 60, w + 59, 139], fill=(255, 20, 50, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    ox, oy = int(cx - sh.width / 2), int(y - 100)
    c = sh.crop((max(0, -ox), max(0, -oy), sh.width, min(sh.height, H - oy)))
    fr.alpha_composite(c, (max(0, ox), max(0, oy)))
GL_FLEX = [(0, 0)]
GL_SQ = [(0, 0), (1, 0)]
deep = R.ANIM['squat'].index(R.ANIM['deep'][0])
# ---- A: reference-like ----
fr = bg()
for x, fl in ((390, False), (1530, True)):
    shadow(fr, x, 975, 360); put(fr, sprite('squat', deep, 560, GL_SQ, flip=fl), x, 1035)
shadow(fr, 960, 1000, 420); put(fr, sprite('flex', 4, 830, GL_FLEX), 960, 1060)
t1 = txt('50 SQUATS', 120, stroke=9, glow=10); t2 = txt('EVERY DAY', 96, stroke=0)
tot = t1.width + 40 + t2.width + 72
x0 = 960 - tot / 2
fr.alpha_composite(t1, (int(x0), int(105 - t1.height / 2)))
pill(fr, t2, x0 + t1.width + 40 + (t2.width + 72) / 2, 105)
fr.convert('RGB').save('cover_A.png')
# ---- B: day 1 vs day 30 ----
fr = bg()
d = ImageDraw.Draw(fr)
for i in range(0, H, 14): d.line([(958, i), (962, i + 7)], fill=(255, 40, 70, 200), width=3)
shadow(fr, 500, 1000, 360); put(fr, sprite('point', 0, 760), 500, 1040)
shadow(fr, 1420, 1005, 420); put(fr, sprite('flex', 4, 860, GL_FLEX), 1420, 1065)
pill(fr, txt('DAY 1', 70, stroke=0), 500, 120, fill=(40, 10, 16))
pill(fr, txt('DAY 30', 70, stroke=0), 1420, 120)
big = txt('50', 260, stroke=12, glow=18); fr.alpha_composite(big, (int(960 - big.width / 2), 330))
s = txt('SQUATS/DAY', 64, stroke=7); fr.alpha_composite(s, (int(960 - s.width / 2), 600))
fr.convert('RGB').save('cover_B.png')
# ---- C: minimal big number ----
fr = bg()
shadow(fr, 1360, 990, 480); put(fr, sprite('squat', deep, 760, GL_SQ), 1360, 1045)
big = txt('50', 400, stroke=14, glow=22); fr.alpha_composite(big, (110, 140))
l2 = txt('SQUATS', 120, stroke=9); fr.alpha_composite(l2, (130, 140 + big.height - 30))
pill(fr, txt('EVERY DAY?', 80, stroke=0), 130 + 300, 140 + big.height + l2.height + 40)
fr.convert('RGB').save('cover_C.png')
