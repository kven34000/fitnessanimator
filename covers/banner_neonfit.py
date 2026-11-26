# NeonFit channel banner 2560x1440 from Magnific art (jUIqdHYLD0, Relax) + text inside the 1546x423 safe band.
import sys
sys.path.insert(0, '/home/claude/work')
import render_v2 as R
from PIL import Image, ImageFilter
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/bnB.png'
W, H = 2560, 1440
art = Image.open(SRC).convert('RGB')
bg = art.resize((W, int(art.height * W / art.width)), Image.LANCZOS).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(22))
bg = Image.eval(bg, lambda v: int(v * 0.55))
sc = 0.78; fg = art.resize((int(W * sc), int(art.height * W / art.width * sc)), Image.LANCZOS)
# feathered edge mask so the smaller foreground melts into the blurred background
import numpy as np
m = np.ones((fg.height, fg.width), np.float32); f = 160
for i in range(f):
    k = i / f; m[:, i] *= k; m[:, -1 - i] *= k; m[i, :] *= k; m[-1 - i, :] *= k
mask = Image.fromarray((m * 255).astype('uint8'))
HX = 1720  # hero centre x (to the right of the name)
can = bg.copy(); can.paste(fg, (HX - fg.width // 2, 230), mask)
can = can.convert('RGBA')
def txt(t, size, col=(255, 255, 255), stroke=8, glow=18):
    return R.text_img(t, R.font(R.F_RUSSO, size), col + (255,), stroke=stroke, stroke_fill=(0, 0, 0), glow=glow, glowcol=R.RED)
# left: name ; right: slogan  (band x 507..2053, y 508..931)
a = txt('NEON', 150); b = txt('FIT', 150, (90, 255, 120))
x0 = 540; y0 = 535
can.alpha_composite(a, (x0, y0)); can.alpha_composite(b, (x0 + a.width - 30, y0))
s1 = txt('HONEST FITNESS', 64); s2 = txt('ANIMATED', 64, (255, 60, 80))
xr = 560
can.alpha_composite(s1, (xr, 705)); can.alpha_composite(s2, (xr, 705 + s1.height - 14))
can.convert('RGB').save('banner_neonfit.jpg', quality=92)
can.convert('RGB').crop((0, 508, W, 931)).resize((1280, 212)).save('/tmp/banner_desktop.png')
print('ok')
