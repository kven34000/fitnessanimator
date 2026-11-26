# English YouTube covers: Magnific Relax art (covers/art/NN.png, no text) + text overlay.
#   python3 covers/covers_en.py  -> covers/en/NN.jpg (1280x720)
# Art IDs in SOURCES.json "covers_en"; reference thumbnails of the RU originals in covers/ref/.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__))
FONT = '/home/claude/fitnessanimator/engine/fonts/Russo.ttf'
if not os.path.exists(FONT): FONT = '/home/claude/work/fonts/Russo.ttf'
W, H = 1280, 720
RED, GREEN, WHITE, BLACK, YEL = (235, 30, 55), (60, 220, 80), (255, 255, 255), (0, 0, 0), (255, 214, 0)
def f(s): return ImageFont.truetype(FONT, s)
def text(im, xy, s, size, fill=WHITE, stroke=8, anchor='la', shadow=True, maxw=None):
    fn = f(size)
    if maxw:
        while ImageDraw.Draw(im).textlength(s, font=fn) > maxw and size > 20: size -= 4; fn = f(size)
    if shadow:
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
        d.text((xy[0] + 6, xy[1] + 8), s, font=fn, fill=(0, 0, 0, 200), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text(xy, s, font=fn, fill=fill + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=BLACK + (255,))
    return ImageDraw.Draw(im).textbbox(xy, s, font=fn, anchor=anchor, stroke_width=stroke)
def pill(im, xy, s, size, bg=YEL, fg=BLACK, anchor='la', pad=(22, 10), r=16, outline=WHITE):
    fn = f(size); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = d.textbbox(xy, s, font=fn, anchor=anchor)
    d.rounded_rectangle([x0 - pad[0], y0 - pad[1], x1 + pad[0], y1 + pad[1]], r, fill=bg + (255,), outline=outline + (255,) if outline else None, width=4)
    d.text(xy, s, font=fn, fill=fg + (255,), anchor=anchor)
def box(im, cx, y, s1, s2, size=54, col=RED):
    fn, fn2 = f(size), f(int(size * 0.42)); d = ImageDraw.Draw(im)
    w = max(d.textlength(s1, font=fn), d.textlength(s2, font=fn2)) + 50
    d.rectangle([cx - w / 2, y, cx + w / 2, y + size * 1.75], fill=(250, 250, 250, 255), outline=BLACK + (255,), width=5)
    d.text((cx, y + 8), s1, font=fn, fill=BLACK + (255,), anchor='ma')
    d.text((cx, y + size * 1.12), s2, font=fn2, fill=col + (255,), anchor='ma')
def art(n):
    return Image.open(f'{D}/art/{n}.png').convert('RGBA').resize((W, H), Image.LANCZOS)
def grad(im, top=True, h=200, a=200):
    g = Image.new('L', (1, h)); g.putdata([int(a * (1 - i / h)) if top else int(a * i / h) for i in range(h)])
    g = g.resize((W, h)); blk = Image.new('RGBA', (W, h), (0, 0, 0, 255)); blk.putalpha(g)
    im.alpha_composite(blk, (0, 0 if top else H - h))
C = {}
def c01(im):
    grad(im, True, 170, 170)
    text(im, (40, 30), '50 SQUATS', 92, maxw=500)
    pill(im, (1240, 40), 'EVERY DAY', 66, anchor='ra')
C['01'] = c01
def c02(im):
    grad(im, True, 230, 150)
    text(im, (40, 26), 'START', 110)
    text(im, (40, 140), 'NOW', 120, fill=RED)
C['02'] = c02
def c03(im):
    grad(im, True, 210, 190)
    text(im, (640, 22), '100 / 100 / 100', 88, anchor='ma', maxw=1180)
    pill(im, (640, 128), '30 DAYS', 58, anchor='ma', bg=RED, fg=WHITE)
C['03'] = c03
def c04(im):
    box(im, 320, 6, 'RUNNING', '(NO DISCIPLINE)', 46)
    box(im, 960, 6, 'WALKING', '(WITH DISCIPLINE)', 46, col=(20, 150, 50))
C['04'] = c04
def c05(im):
    d = ImageDraw.Draw(im)
    d.rectangle([30, 28, 560, 128], fill=(245, 245, 245, 255), outline=BLACK + (255,), width=6)
    d.text((52, 78), 'STRENGTH', font=f(64), fill=BLACK + (255,), anchor='lm')
    d.rectangle([400, 50, 540, 106], outline=BLACK + (255,), width=4); d.rectangle([406, 56, 430, 100], fill=RED + (255,))
C['05'] = c05
def c06(im):
    text(im, (1240, 230), 'HOW', 150, anchor='ra')
    text(im, (1240, 390), 'LONG?', 150, fill=RED, anchor='ra')
C['06'] = c06
def c07(im):
    grad(im, False, 300, 210)
    text(im, (640, 470), 'WHAT ACTUALLY', 84, anchor='ma')
    text(im, (640, 560), 'WORKS?', 92, anchor='ma', fill=YEL)
    text(im, (30, 690), 'CALISTHENICS', 46, anchor='ld')
    text(im, (1250, 690), 'GYM', 58, anchor='rd', fill=RED)
C['07'] = c07
def c08(im):
    text(im, (320, 34), '10 PUSH-UPS', 70, anchor='ma', maxw=600)
    text(im, (960, 34), '80 PUSH-UPS', 70, anchor='ma', fill=WHITE, maxw=600)
C['08'] = c08
def c09(im):
    # whiteboard area (art 09: white board ~ x 360..880, y 60..500 at 1280x720)
    d = ImageDraw.Draw(im)
    d.text((612, 120), 'MORNING', font=f(92), fill=BLACK + (255,), anchor='ma')
    d.text((612, 232), 'CALISTHENICS', font=f(62), fill=RED + (255,), anchor='ma')
    pill(im, (612, 340), '5 MINUTES', 56, bg=BLACK, fg=WHITE, anchor='ma', outline=None)
C['09'] = c09
if __name__ == '__main__':
    os.makedirs(f'{D}/en', exist_ok=True)
    for n, fn in sorted(C.items()):
        if not os.path.exists(f'{D}/art/{n}.png'): print('skip', n); continue
        im = art(n); fn(im); im.convert('RGB').save(f'{D}/en/{n}.jpg', quality=92); print(n)
