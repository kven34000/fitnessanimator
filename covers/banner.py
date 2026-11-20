import sys; sys.path.insert(0, '/home/claude/work'); sys.path.insert(0, '/home/claude/cover')
import render_v2 as R
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
R.init()
W, H = 2560, 1440
SX, SY, SW, SH = (W - 1546) // 2, (H - 423) // 2, 1546, 423
def base():
    bg = R.BG.convert('RGBA').resize((W, int(W * 1080 / 1920)), Image.LANCZOS)
    fr = Image.new('RGBA', (W, H), (0, 0, 0, 255)); fr.alpha_composite(bg, (0, (H - bg.height) // 2 - 80))
    gl = R.GLOW.resize(bg.size, Image.LANCZOS); fr.alpha_composite(gl, (0, (H - bg.height) // 2 - 80))
    return fr
def spr(name, idx, h, glow=None, flip=False, dim=1.0):
    big, fx, fy, mk, im = R.ANIM[name][idx]
    s_ = R.apply_glow(big, mk, glow, 10.0) if glow else big
    s = h / s_.height
    o = s_.resize((int(s_.width * s), int(s_.height * s)), Image.LANCZOS)
    if flip: o = o.transpose(Image.FLIP_LEFT_RIGHT)
    if dim < 1:
        a = np.array(o).astype(float); a[..., :3] *= dim; a[..., 3] *= 0.85; o = Image.fromarray(a.astype(np.uint8))
    return o
def put(fr, im, cx, bottom): fr.alpha_composite(im, (int(cx - im.width / 2), int(bottom - im.height)))
def txt(t, size, col=(255, 255, 255), stroke=7, glow=0):
    return R.text_img(t, R.font(R.F_RUSSO, size), col + (255,), stroke=stroke, stroke_fill=(0, 0, 0), glow=glow, glowcol=R.RED)
def pill(fr, im, x, cy, fill=R.RED):
    d = ImageDraw.Draw(fr); w, h = im.width + 56, im.height + 24
    d.rounded_rectangle([x, cy - h / 2, x + w, cy + h / 2], 22, fill=fill + (255,), outline=(255, 255, 255, 255), width=4)
    fr.alpha_composite(im, (int(x + 28), int(cy - im.height / 2)))
deep = R.ANIM['squat'].index(R.ANIM['deep'][0])
def make(lines, tag, out):
    fr = base()
    bot = SY + SH + 6
    # dim outer figures (visible on desktop/TV only)
    put(fr, spr('run', 2, 380, dim=0.35), SX - 200, bot)
    put(fr, spr('box', 0, 400, dim=0.35), SX + SW + 200, bot)
    # main figures in safe area, right side
    put(fr, spr('squat', deep, 330, [(0, 0), (1, 0)]), SX + SW - 520, bot - 4)
    put(fr, spr('flex', 4, 440, [(0, 0)]), SX + SW - 270, bot + 10)
    put(fr, spr('back', 3, 410, [(1, 0)]), SX + SW - 60, bot)
    # text left
    y = SY + 70
    for i, (t, c) in enumerate(lines):
        im = txt(t, 104, c, glow=10 if i == 0 else 0)
        fr.alpha_composite(im, (SX + 10, int(y - im.height / 2))); y += 118
    pill(fr, txt(tag, 46, stroke=0), SX + 16, y + 20)
    fr.convert('RGB').save(out, quality=92)
make([('ЧЕСТНЫЙ', (255, 255, 255)), ('ФИТНЕС', R.RED2)], 'БЕЗ ВОДЫ • БЕЗ ЗАЛА', 'banner_RU.jpg')
make([('HONEST', (255, 255, 255)), ('FITNESS', R.RED2)], 'NO FLUFF • NO GYM', 'banner_EN.jpg')
# preview with safe area outline
im = Image.open('banner_RU.jpg'); d = ImageDraw.Draw(im)
d.rectangle([SX, SY, SX + SW, SY + SH], outline=(0, 255, 255), width=4)
d.rectangle([(W - 2560) // 2, SY, W, SY + SH], outline=(255, 255, 0), width=2)
im.resize((1280, 720)).save('/tmp/banner_prev.png')
