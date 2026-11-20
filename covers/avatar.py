import sys; sys.path.insert(0, '/home/claude/work')
import render_v2 as R
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
S = 1600
src = Image.open('/home/claude/p2d/spr/flex/f0.png').convert('RGBA')
w, h = src.size
# head+shoulders+pecs crop
crop = src.crop((int(w * 0.02), 0, int(w * 0.98), int(h * 0.40)))
sc = S * 0.98 / crop.width
fig = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
# background: dark with red radial glow + grid hint
bg = Image.new('RGBA', (S, S), (8, 2, 4, 255))
yy, xx = np.mgrid[0:S, 0:S]
r = np.sqrt((xx - S / 2) ** 2 + (yy - S * 0.42) ** 2) / (S * 0.55)
g = np.clip(1 - r, 0, 1) ** 1.6
arr = np.array(bg).astype(float)
arr[..., 0] += 200 * g; arr[..., 1] += 10 * g; arr[..., 2] += 30 * g
bg = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
# neon rim around figure
al = fig.split()[3]
pad = Image.new('L', (S, S), 0); ox = (S - fig.width) // 2; oy = int(S * 0.08)
pad.paste(al, (ox, oy))
rim = Image.new('RGBA', (S, S), R.RED + (0,))
rim.putalpha(pad.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(22)).point(lambda v: min(255, int(v * 1.4))))
bg.alpha_composite(rim)
bg.alpha_composite(fig, (ox, oy))
# fade bottom to dark so the cut torso blends
fade = Image.new('RGBA', (S, S), (0, 0, 0, 0)); fa = np.zeros((S, S), np.uint8)
y0 = int(S * 0.80); fa[y0:] = np.linspace(0, 235, S - y0)[:, None].astype(np.uint8)
fade.putalpha(Image.fromarray(fa)); bg.alpha_composite(fade)
# circular neon ring (shows inside YouTube's circle crop)
d = ImageDraw.Draw(bg)
bg.convert('RGB').resize((800, 800), Image.LANCZOS).save('avatar_800.png')
print(fig.size, sc)
