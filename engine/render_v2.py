import math, random, random, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from multiprocessing import Pool
sys.path.insert(0, '/home/claude/work')
from words import W

WD, HT, FPS = 1920, 1080, 30
DUR = 92.0
RED = (255, 30, 60)
RED2 = (255, 70, 90)
F_RUSSO = '/home/claude/work/fonts/Russo.ttf'
F_M900 = '/home/claude/work/fonts/Mont900.ttf'
F_M800 = '/home/claude/work/fonts/Mont800.ttf'
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

# ---------------- easing ----------------
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def out_back(t, s=1.9):
    t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def out_cubic(t): t = clamp(t) - 1; return t * t * t + 1
def in_cubic(t): t = clamp(t); return t * t * t

# ---------------- poses ----------------
POSE = dict(think=0, point=1, cross=2, flex=3, thumbflex=4, thumb=5, side=6, half=7, deep=8,
            ok=9, box=10, run=11, lie=12, back=13)
S0 = 820 / 1354.0  # uniform scale: standing pose -> 820 px tall
SPR = {}

SPRDIR='/home/claude/p2d/spr'
SUB_LABELS=('ПОДПИСАТЬСЯ','ЛАЙК')
DAY_LABEL='ДЕНЬ'
PROPS={}
EXTRA={}
CAM=[]
CAM_FLOOR=None
CAM_MAXZ=9.0
SUBDODGE=False; _CHR=[]
def sub_y(t, tot):
    if not SUBDODGE or not _CHR: return 1030
    q = 8; m = Image.new('L', (WD // q, HT // q), 0)
    for al, (x, y) in _CHR:
        a = al.resize((max(1, al.width // q), max(1, al.height // q))).point(lambda v: 255 if v > 200 else 0)
        m.paste(255, (x // q, y // q), a)
    if CAM:
        z, cx, cy = cam_state(t)
        if abs(z - 1) > 0.002:
            w, h = WD / z, HT / z
            x0 = min(max(cx - w / 2, 0), WD - w); y0 = min(max(cy - h / 2, 0), HT - h)
            m = m.transform(m.size, Image.EXTENT, (x0 / q, y0 / q, (x0 + w) / q, (y0 + h) / q))
    a = np.array(m) > 0; x0 = int((WD / 2 - tot / 2 - 20) / q); x1 = int((WD / 2 + tot / 2 + 20) / q)
    if a[int(995 / q):int(1065 / q), x0:x1].sum() < 3: return 1030
    if a[int(25 / q):int(95 / q), x0:x1].sum() < 3: return 60
    return 1030
CAMSENT=dict(k='__cam__', t0=-1, t1=1e9)
UIK={'chip','title','big','sub','count','days','blocks','inset','card','bubble','calendar','countdown'}
def cam_state(t):
    z, cx, cy = 1.0, WD / 2, HT / 2
    for (t0, t1, x, y, zz, ein, eout) in CAM:
        if t0 - 0.0 <= t < t1:
            k = clamp((t - t0) / ein) if ein > 0 else 1.0
            if eout > 0: k = min(k, clamp((t1 - t) / eout))
            k = k * k * (3 - 2 * k)
            zz = min(zz, CAM_MAXZ); z = 1 + (zz - 1) * k; cx = WD / 2 + (x - WD / 2) * k; cy = HT / 2 + (y - HT / 2) * k
    return z, cx, cy
def apply_cam(fr, t):
    z, cx, cy = cam_state(t)
    if abs(z - 1) < 0.002: return fr
    w, h = WD / z, HT / z
    x0 = min(max(cx - w / 2, 0), WD - w); y0 = min(max(cy - h / 2, 0), HT - h)
    if CAM_FLOOR: y0 = min(max(y0, CAM_FLOOR - 975 / z), HT - h)
    # (zoom is capped at CAM_MAXZ so the whole figure stays in frame above the subtitles)
    return fr.transform((WD, HT), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BILINEAR)
LOCS={}
ANIM={}
SHEETMAP=dict(think=('think',[4,5,6,7]),point=('point',None),cross=('cross',None),flex=('flex',[0,1,2,3,4,6,7]),thumbflex=('thumbflex',[0,1,2,3,4,6,7]),
  thumb=('ok',[0,1,2,3,4,7]),ok=('ok',[0,1,2,3,4,7]),back=('back',None),run=('run',None),lie=('lie',None),box=('box',None),squat=('squat',[0,1,2,4,3,5,6,7]))
def _mk(im, mk=None):
    a = np.array(im.split()[3]); h = a.shape[0]
    ys, xs = np.nonzero(a[int(h * 0.94):] > 128); fx = xs.mean() if len(xs) else im.width / 2
    pad = 60
    big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    al = Image.new('L', big.size, 0); al.paste(im.split()[3], (pad, pad))
    g1 = al.filter(ImageFilter.GaussianBlur(18))
    g2 = al.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))
    glow = Image.new('RGBA', big.size, RED + (0,))
    glow.putalpha(ImageChops.add(g1.point(lambda v: int(v * 0.9)), g2.point(lambda v: int(v * 0.85))))
    big = Image.alpha_composite(big, glow); big.alpha_composite(im, (pad, pad))
    mbig = None
    if mk is not None:
        ma = np.zeros((big.size[1], big.size[0], 4), np.float32)
        ma[pad:pad + mk.size[1], pad:pad + mk.size[0]] = np.dstack([np.array(c) for c in mk.split()]).astype(np.float32)
        ma *= (np.array(al).astype(np.float32) / 255)[..., None]
        mbig = ma.astype(np.uint8)
    return (big, fx + pad, im.height + pad, mbig, im)

def load_sprites():
    cache = {}
    for name, (sheet, idx) in SHEETMAP.items():
        key = (sheet, tuple(idx) if idx else None)
        if key not in cache:
            ids = idx or list(range(8))
            import os
            ims = [Image.open(f'{SPRDIR}/{sheet}/f{i}.png').convert('RGBA') for i in ids]
            mks = [Image.open(f'{SPRDIR}/{sheet}/f{i}_m.png').convert('RGBA') if os.path.exists(f'{SPRDIR}/{sheet}/f{i}_m.png') else None for i in ids]
            ref = sorted(i.height for i in ims)[len(ims) // 2]
            norm = sheet in ('ok',)
            sc = (780 / ref) if sheet != 'run' else (760 / ref)
            if sheet == 'lie': sc = 820 / ims[0].width
            frs = []
            for im, mk in zip(ims, mks):
                s2 = (sc * ref / im.height) if norm else sc
                sz = (max(1, int(im.width * s2)), max(1, int(im.height * s2)))
                im = im.resize(sz, Image.LANCZOS)
                if mk is not None: mk = Image.merge('RGBA', [c.resize(sz, Image.BILINEAR) for c in mk.split()])
                frs.append(_mk(im, mk))
            cache[key] = frs
        ANIM[name] = cache[key]
    for nm, k in (('side', 0), ('half', 5), ('deep', 7)):
        ANIM[nm] = [ANIM['squat'][k]]
    for nm in ANIM: SPR[nm] = ANIM[nm][0][:3]
    for k in range(8):
        im = Image.open(f'{SPRDIR}/props/f{k}.png').convert('RGBA'); PROPS[k] = im

GLOWC = (40, 255, 110)
def apply_glow(spr, mk, glow, t):
    if not glow or mk is None: return spr
    w = np.zeros(mk.shape[:2], np.float32)
    for ch, t_on in glow:
        k = clamp((t - t_on) / 0.25)
        if k <= 0: continue
        pul = 0.82 + 0.18 * math.sin((t - t_on) * 7)
        w = np.maximum(w, mk[..., ch].astype(np.float32) / 255 * k * pul)
    if w.max() <= 0.01: return spr
    arr = np.array(spr).astype(np.float32)
    lum = (arr[..., 0] * 0.3 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11) / 255
    tgt = np.stack([GLOWC[0] * (0.35 + 0.65 * lum), GLOWC[1] * (0.55 + 0.45 * lum), GLOWC[2] * (0.45 + 0.55 * lum)], -1)
    a = (w * 0.82)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - a) + tgt * a
    out = Image.fromarray(arr.clip(0, 255).astype(np.uint8), 'RGBA')
    halo = Image.fromarray((w * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(10))
    hl = Image.new('RGBA', out.size, GLOWC + (0,)); hl.putalpha(halo.point(lambda v: int(v * 0.7)))
    base = Image.new('RGBA', out.size, (0, 0, 0, 0)); base.alpha_composite(out); base.alpha_composite(hl)
    return base

def frame_for(pose, a, e):
    frs = ANIM[pose]; n = len(frs)
    if n == 1: return frs[0]
    if pose == 'run': return frs[int(a * 15) % n]
    if pose == 'squat':
        P = e.get('period', 1.1); ph = (a % P) / P
        if ph < 0.42: k = int(ph / 0.42 * 8)
        elif ph < 0.50: k = 7
        elif ph < 0.88: k = 7 - int((ph - 0.5) / 0.38 * 8)
        else: k = 0
        return frs[max(0, min(7, k))]
    peak = n // 2
    intro = 0.45
    if a < intro: return frs[min(peak, int(a / intro * (peak + 1)))]
    cyc = [peak - 1, peak, peak + 1 if peak + 1 < n else peak, peak]
    return frs[cyc[int((a - intro) / 0.32) % 4]]

# ---------------- background ----------------
BG = None
def make_bg():
    y, x = np.mgrid[0:HT, 0:WD].astype(np.float32)
    base = np.zeros((HT, WD, 3), np.float32)
    base[:] = (10, 3, 6)
    # top-down dark gradient
    base *= (0.75 + 0.25 * (y / HT))[..., None]
    # floor grid (perspective) below horizon
    hor = 760
    img = Image.fromarray(base.clip(0, 255).astype(np.uint8))
    lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(-14, 15):
        x0 = WD / 2 + k * 60; x1 = WD / 2 + k * 420
        d.line([(x0, hor), (x1, HT)], fill=RED + (55,), width=2)
    for j in range(1, 12):
        yy = hor + (HT - hor) * (j / 11) ** 1.8
        d.line([(0, yy), (WD, yy)], fill=RED + (int(25 + 45 * j / 11),), width=2)
    d.line([(0, hor), (WD, hor)], fill=RED + (150,), width=3)
    lay = Image.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)), lay)
    # fade grid to edges
    fade = np.clip(1 - (np.abs(x - WD / 2) / (WD * 0.62)) ** 2, 0, 1)
    la = np.array(lay); la[..., 3] = (la[..., 3] * fade).astype(np.uint8)
    img = Image.alpha_composite(img.convert('RGBA'), Image.fromarray(la))
    # back wall: thin neon stripes
    d2 = ImageDraw.Draw(img)
    for yy in (140, 165):
        d2.line([(0, yy), (WD, yy)], fill=(80, 10, 25, 255), width=2)
    # vignette
    v = ((x - WD / 2) / (WD / 1.6)) ** 2 + ((y - HT / 2) / (HT / 1.25)) ** 2
    vig = np.clip(1 - v * 0.75, 0.25, 1)
    arr = np.array(img).astype(np.float32); arr[..., :3] *= vig[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGBA')

GLOW = None
def make_glow():
    y, x = np.mgrid[0:HT, 0:WD].astype(np.float32)
    r = np.sqrt(((x - WD / 2) / 700) ** 2 + ((y - 560) / 480) ** 2)
    a = np.clip(1 - r, 0, 1) ** 2 * 120
    g = np.zeros((HT, WD, 4), np.uint8); g[..., 0] = 255; g[..., 1] = 20; g[..., 2] = 50; g[..., 3] = a.astype(np.uint8)
    return Image.fromarray(g)

random.seed(7)
PARTS = [(random.uniform(0, WD), random.uniform(0, HT), random.uniform(10, 40), random.uniform(1.5, 4), random.uniform(0, 6.28)) for _ in range(70)]

# ---------------- timeline ----------------
EL = []
def char(pose, t0, t1, x=960, y=968, sc=1.0, enter='pop', exit='fade', flip=False, ghost=False, burn=False, zoom=0.0, glow=None):
    EL.append(dict(k='char', pose=pose, t0=t0, t1=t1, x=x, y=y, sc=sc, enter=enter, exit=exit, flip=flip, ghost=ghost, burn=burn, zoom=zoom, glow=glow))
def prop(idx, t0, t1, x, y, sc=0.4, strike=False):
    EL.append(dict(k='prop', idx=idx, t0=t0, t1=t1, x=x, y=y, sc=sc, strike=strike))
def squat(t0, t1, x=960, y=968, sc=1.0, period=1.0, enter='pop', exit='fade', glow=None):
    EL.append(dict(k='squat', t0=t0, t1=t1, x=x, y=y, sc=sc, period=period, enter=enter, exit=exit, glow=glow))
def chip(text, t0, t1, x, y, style='n', size=46, anchor='l'):
    if anchor == 'l':
        try: x = max(10, min(x, WD - 90 - chip_img(text, size, style).width + 44))
        except Exception: pass
    EL.append(dict(k='chip', text=text, t0=t0, t1=t1, x=x, y=y, style=style, size=size, anchor=anchor))
def title(text, t0, t1, x=960, y=120, size=96, type_=True, anchor='c', col=(255, 255, 255)):
    if y <= 160: y -= 40
    EL.append(dict(k='title', text=text, t0=t0, t1=t1, x=x, y=y, size=size, type=type_, anchor=anchor, col=col))
def big(text, t0, t1, x=960, y=330, size=230):
    EL.append(dict(k='big', text=text, t0=t0, t1=t1, x=x, y=y, size=size))
def xmark(t0, t1, cx=960, cy=560, s=360):
    EL.append(dict(k='x', t0=t0, t1=t1, cx=cx, cy=cy, s=s))
def stairs(t0, t1):
    EL.append(dict(k='stairs', t0=t0, t1=t1))
def subbtn(t0, t1, x, y):
    EL.append(dict(k='sub', t0=t0, t1=t1, x=x, y=y))
SHAKES = []

# 1 hook
char('think', 0.0, 1.4, enter='pop', sc=0.84)
squat(1.4, 3.6, x=760, sc=0.84, period=0.75, enter='pop')
EL.append(dict(k='days', t0=2.7, t1=3.6, x=1270, y=560))
title('50 ПРИСЕДАНИЙ', 1.3, 3.6, y=110, size=110)
title('КАЖДЫЙ ДЕНЬ', 2.7, 3.6, y=225, size=70, col=RED2)
# 2
char('point', 3.6, 7.45, enter='pop', sc=0.95)
chip('ШТАНГА', 3.9, 7.45, 1250, 380, 'strike', 54)
prop(1, 3.9, 7.45, 1720, 385, 0.42, strike=True)
chip('ЗАЛ', 4.95, 7.45, 1250, 490, 'strike', 54)
prop(4, 4.95, 7.45, 1720, 560, 0.30, strike=True)
chip('ТОЛЬКО ТЫ + ТЕЛО', 6.0, 7.45, 1250, 600, 'on', 54)
# 3
char('cross', 7.45, 11.85, enter='pop', zoom=0.0)
title('ДОСМОТРИ ДО КОНЦА', 7.6, 11.85, y=120, size=90)
# 4-5 squats + muscles
squat(11.85, 19.8, x=700, period=1.1, enter='left', glow=[(0, 16.5), (1, 17.1), (2, 17.95)])
char('back', 13.5, 19.8, x=1440, enter='right', sc=0.95, glow=[(0, 16.5), (1, 17.1), (2, 18.85)])
chip('НОГИ', 16.5, 19.8, 40, 300, 'on', 44)
chip('ЯГОДИЦЫ', 17.1, 19.8, 40, 390, 'on', 44)
chip('КОРПУС', 17.95, 19.8, 40, 480, 'on', 44)
chip('ПОЯСНИЦА', 18.85, 19.8, 40, 570, 'on', 44)
title('С СОБСТВЕННЫМ ВЕСОМ', 14.6, 16.4, y=120, size=80)
# 6 anywhere
squat(19.8, 23.85, x=560, period=1.1, enter='none')
char('thumbflex', 19.9, 23.85, x=1450, enter='right', sc=0.95)
title('ГДЕ УГОДНО', 21.5, 23.85, x=1450, y=105, size=72, col=(255, 255, 255))
title('КОГДА УГОДНО', 22.55, 23.85, x=1450, y=190, size=72, col=RED2)
# 7 week 1
big('НЕДЕЛЯ 1', 23.95, 25.2, size=210)
char('deep', 25.2, 27.35, x=960, enter='pop', burn=True, glow=[(0, 25.75)])
chip('ГОРЯТ НОГИ', 25.75, 27.35, 1300, 420, 'on', 52)
char('ok', 27.35, 31.15, enter='pop', glow=[(2, 28.6)])
chip('ЭТО НОРМАЛЬНО', 27.6, 31.15, 1240, 380, 'on', 52)
chip('МЫШЦЫ РАСТУТ', 28.6, 31.15, 1240, 490, 'n', 52)
# 8 week 2
big('НЕДЕЛЯ 2', 31.15, 32.35, size=210)
stairs(32.35, 37.6)
char('run', 32.35, 37.6, x=1250, y=900, enter='right', sc=0.92)
chip('СТАБИЛЬНЕЕ', 32.8, 37.6, 80, 300, 'on', 52)
chip('УВЕРЕННЕЕ', 34.08, 37.6, 80, 410, 'on', 52)
chip('ЛЕСТНИЦА ЛЕГЧЕ', 36.9, 37.6, 80, 520, 'on', 52)
# 9 week 3
big('НЕДЕЛЯ 3', 37.6, 38.85, size=210)
char('thumb', 38.85, 42.9, enter='pop')
chip('БАЛАНС', 38.96, 42.9, 1260, 330, 'on', 52)
chip('КООРДИНАЦИЯ', 39.52, 42.9, 1260, 440, 'on', 52)
chip('ВЫНОСЛИВОСТЬ', 40.4, 42.9, 1260, 550, 'on', 52)
# 10 month
big('1 МЕСЯЦ', 42.9, 43.7, size=210)
squat(43.7, 46.35, x=960, period=0.6, enter='pop')
chip('= РАЗМИНКА', 45.5, 46.35, 1340, 420, 'on', 56)
char('flex', 46.35, 50.5, x=680, enter='left', sc=0.95, glow=[(0, 46.6)])
char('back', 46.6, 50.5, x=1300, enter='right', sc=0.95, glow=[(0, 46.6), (2, 47.5)])
chip('НОГИ СИЛЬНЕЕ', 46.6, 50.5, 60, 150, 'on', 46)
chip('ОСАНКА РОВНЕЕ', 47.5, 50.5, 1440, 150, 'on', 42)
# 11 honest
char('think', 50.5, 54.05, enter='pop')
title('ЧЕСТНО:', 50.6, 54.05, y=120, size=90, col=RED2)
xmark(52.0, 54.05, cx=1450, cy=600, s=300)
chip('БОДИБИЛДЕР', 51.9, 54.05, 1270, 360, 'strike', 54)
# 12 add weight
char('point', 54.05, 58.25, enter='pop', sc=0.95)
title('ХОЧЕШЬ МАССУ?', 54.1, 58.25, y=120, size=90)
chip('ГАНТЕЛИ', 56.1, 58.25, 1270, 330, 'on', 54)
prop(0, 56.1, 58.25, 1720, 330, 0.36)
chip('ШТАНГА', 56.7, 58.25, 1270, 440, 'on', 54)
prop(1, 56.7, 58.25, 1720, 445, 0.36)
chip('РЕЗИНА', 57.55, 58.25, 1270, 550, 'on', 54)
prop(2, 57.55, 58.25, 1720, 560, 0.34)
# 13 base = top
char('thumb', 58.25, 64.7, enter='pop', glow=[(0, 63.28), (1, 63.76)])
big('ТОП', 59.8, 60.5, x=1440, y=300, size=210)
chip('ПОДВИЖНОСТЬ', 60.4, 64.7, 60, 300, 'on', 46)
chip('ГИБКОСТЬ', 61.2, 64.7, 60, 400, 'on', 46)
chip('КРОВООБРАЩЕНИЕ', 61.8, 64.7, 60, 500, 'on', 46)
chip('КОЛЕНИ', 63.28, 64.7, 1440, 340, 'on', 46)
chip('ГОЛЕНОСТОП', 63.76, 64.7, 1440, 440, 'on', 46)
SHAKES.append((59.84, 0.35))
# 14 confidence
char('flex', 64.7, 71.5, enter='pop', ghost=True, sc=0.84, glow=[(1, 65.9), (3, 65.9)])
title('УВЕРЕННОСТЬ', 65.9, 71.5, y=130, size=110, col=RED2)
title('КОНТРОЛЬ НАД ЖИЗНЬЮ', 70.2, 71.5, y=235, size=60)
SHAKES.append((65.92, 0.25))
# 15 worth it
char('lie', 71.5, 74.65, x=960, y=900, enter='pop')
chip('НЕ СТОИТ', 71.95, 74.65, 640, 360, 'dimx', 54, anchor='c')
chip('СТОИТ', 72.05, 74.65, 1280, 360, 'check', 54, anchor='c')
# 16 tips
char('cross', 74.65, 77.3, enter='pop')
chip('50 — МНОГО?', 74.7, 77.3, 1250, 360, 'n', 54)
chip('ДЕЛИ: 5 × 10', 76.24, 77.3, 1250, 470, 'on', 54)
char('flex', 77.3, 82.0, enter='pop', sc=0.82)
title('75–100', 78.6, 82.0, y=150, size=150, col=RED2)
title('КАЖДЫЙ ДЕНЬ', 80.2, 82.0, y=280, size=70)
# 17 subscribe
char('box', 82.0, 87.45, enter='pop', sc=1.1)
subbtn(82.0, 87.45, 960, 0)
chip('СКОЛЬКО ПРИСЕДАЕШЬ ТЫ?', 84.8, 87.45, 40, 420, 'on', 44)
# 18 outro
char('cross', 87.45, 92.0, enter='pop', ghost=True, sc=0.84)
title('МАЛЕНЬКИЕ ШАГИ', 87.5, 92.0, y=110, size=90)
title('БОЛЬШИЕ ПЕРЕМЕНЫ', 89.45, 92.0, y=220, size=90, col=RED2)

# ---------------- extra visuals ----------------
def fxe(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.insert(0, d)
# locations: anywhere / anytime
fxe('loc', 19.8, 23.85, seq=[(19.8, 'park'), (21.0, 'home'), (21.9, 'office'), (22.55, 'roof')])
fxe('loc', 87.45, 92.0, seq=[(87.45, 'roof')])
# anime speed lines
fxe('speed', 32.35, 37.6, mode='h')
fxe('speed', 43.7, 46.35, mode='r')
fxe('speed', 64.7, 71.5, mode='r')
fxe('burst', 59.8, 60.6)
fxe('burst', 65.88, 66.6)
EL.insert(0, dict(k='fire', t0=25.7, t1=27.35, x=960, y=890))
EL.append(dict(k='plus', t0=28.6, t1=31.15, x=960, y=760))
EL.append(dict(k='bar', t0=40.4, t1=42.9, x=1260, y=680, label=''))
EL.append(dict(k='count', t0=43.75, t1=46.35, x=1450, y=640, n0=0, n1=50))
EL.insert(0, dict(k='bb', t0=51.7, t1=54.05, x=1450, y=968))
EL.append(dict(k='flow', t0=61.8, t1=64.7, x=960, y=968))
EL.append(dict(k='blocks', t0=76.24, t1=77.3, x=1250, y=640))
EL.append(dict(k='phone', t0=82.3, t1=87.45, x=1560, y=700))
PUNCH = [1.3, 3.9, 4.95, 7.6, 16.5, 17.1, 17.95, 18.85, 25.75, 28.6, 45.5, 51.9, 59.84, 65.92, 73.28, 80.2, 89.45]

# ---------------- subtitles ----------------
def build_subs():
    chunks = []; cur = []
    for i, (w, a, b) in enumerate(W):
        cur.append((w, a, b))
        txt = ' '.join(x[0] for x in cur)
        nxt = W[i + 1] if i + 1 < len(W) else None
        brk = (w[-1] in '.,?!:' or w.endswith('...') or len(cur) >= 3 or len(txt) > 20 or
               (nxt and nxt[1] - b > 0.3) or nxt is None)
        if brk:
            chunks.append(cur); cur = []
    out = []
    for j, c in enumerate(chunks):
        s = c[0][1]; e = chunks[j + 1][0][1] if j + 1 < len(chunks) else c[-1][2] + 0.6
        e = min(e, c[-1][2] + 0.6)
        out.append((s, e, c))
    return out
SUBS = build_subs()

# ---------------- drawing helpers ----------------
def text_img(text, f, fill, stroke=0, stroke_fill=(0, 0, 0), glow=0, glowcol=RED):
    bb = f.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 2 * glow + 8, bb[3] - bb[1] + 2 * glow + 8
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = (glow + 4 - bb[0], glow + 4 - bb[1])
    if glow:
        g = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text(o, text, font=f, fill=glowcol + (255,), stroke_width=stroke + 4, stroke_fill=glowcol + (255,))
        g = g.filter(ImageFilter.GaussianBlur(glow / 2)); im = Image.alpha_composite(im, g)
        d = ImageDraw.Draw(im)
    d.text(o, text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

_cache = {}
def cached(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

AUDIT = None; CUR = [None]
def paste_scaled(fr, im, cx, cy, s, alpha=1.0, ax=0.5, ay=0.5):
    if s <= 0.01 or alpha <= 0.01: return
    if AUDIT is not None and CUR[0] is not None:
        w_, h_ = im.width * s, im.height * s; x_, y_ = cx - w_ * ax, cy - h_ * ay
        AUDIT['txt'].append((CUR[0], (x_, y_, x_ + w_, y_ + h_)))
    if abs(s - 1) > 0.003:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if alpha < 0.999:
        a = im.split()[3].point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    fr.alpha_composite(im, (int(cx - im.width * ax), int(cy - im.height * ay)))

def chip_img(text, size, style):
    def mk():
        f = font(F_M900, size)
        bb = f.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]
        padx, pady = 30, 18
        extra = 64 if style in ('check', 'dimx') else 0
        w, h = tw + 2 * padx + extra, th + 2 * pady
        G = 22
        im = Image.new('RGBA', (w + 2 * G, h + 2 * G), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        on = style in ('on', 'check')
        col = RED if style != 'dimx' else (120, 60, 70)
        if style != 'dimx':
            gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
            ImageDraw.Draw(gl).rounded_rectangle([G, G, G + w, G + h], radius=h // 2, outline=col + (255,), width=8)
            im = Image.alpha_composite(im, gl.filter(ImageFilter.GaussianBlur(9))); d = ImageDraw.Draw(im)
        fillc = (40, 4, 12, 235) if not on else (230, 20, 55, 255)
        if style == 'dimx': fillc = (25, 10, 14, 220)
        d.rounded_rectangle([G, G, G + w, G + h], radius=h // 2, fill=fillc, outline=col + (255,), width=4)
        tcol = (255, 255, 255) if style != 'dimx' else (150, 120, 125)
        d.text((G + padx - bb[0] + extra, G + pady - bb[1]), text, font=f, fill=tcol)
        if style == 'check':
            cx, cy = G + padx + 22, G + h // 2
            d.line([(cx - 16, cy), (cx - 4, cy + 13), (cx + 18, cy - 14)], fill=(255, 255, 255), width=8, joint='curve')
        if style == 'dimx':
            cx, cy = G + padx + 22, G + h // 2
            d.line([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill=(200, 60, 80), width=7)
            d.line([(cx - 14, cy + 14), (cx + 14, cy - 14)], fill=(200, 60, 80), width=7)
        return im
    return cached(('chip', text, size, style), mk)

def draw_strike(fr, x0, y0, w, h, p):
    if p <= 0: return
    d = ImageDraw.Draw(fr)
    x1 = x0 + w * p
    d.line([(x0, y0 + h * 0.55), (x1, y0 + h * 0.45)], fill=(255, 255, 255), width=8)
    d.line([(x0, y0 + h * 0.55), (x1, y0 + h * 0.45)], fill=RED, width=4)

def stairs_layer(t, t0):
    lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sw, sh = 150, 70
    off = ((t - t0) * 2.2 % 1.0)
    st = [(1130 + (k - off) * sw, 900 - (k - off) * sh) for k in range(-8, 10)]
    for x, y in st:
        d.polygon([(x, y), (x + sw, y), (x + sw, HT), (x, HT)], fill=(30, 4, 10, 220))
    for x, y in st:
        d.line([(x, y), (x + sw, y)], fill=RED + (255,), width=6)
        d.line([(x + sw, y), (x + sw, y - sh)], fill=RED + (255,), width=6)
    g = lay.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(g, lay)

# ---------------- frame ----------------
def enter_tf(e, t):
    """returns (dx, dy, scale, alpha)"""
    a = t - e['t0']; b = e['t1'] - t
    dx = dy = 0; s = 1; al = 1
    en = e.get('enter', 'pop'); ex = e.get('exit', 'fade')
    if en == 'pop':
        s = out_back(a / 0.32); al = clamp(a / 0.1)
    elif en == 'up':
        dy = (1 - out_cubic(a / 0.35)) * 700
    elif en == 'left':
        dx = -(1 - out_cubic(a / 0.35)) * 1200
    elif en == 'right':
        dx = (1 - out_cubic(a / 0.35)) * 1200
    elif en == 'fade':
        al = clamp(a / 0.6)
    if ex == 'fade' and b < 0.12:
        al *= clamp(b / 0.12); s *= 0.94 + 0.06 * clamp(b / 0.12)
    return dx, dy, s, al

def render(fi):
    t = fi / FPS
    fr = BG.copy()
    # pulsing glow
    pulse = 0.75 + 0.25 * math.sin(t * 2.4)
    # beat pump on music (140bpm)
    beat = (t * 140 / 60) % 1
    pump = 0.15 * math.exp(-beat * 6)
    ga = GLOW.split()[3].point(lambda v: int(min(255, v * (pulse + pump))))
    g = GLOW.copy(); g.putalpha(ga); fr.alpha_composite(g)
    # particles
    d = ImageDraw.Draw(fr)
    for (px, py, sp, r, ph) in PARTS:
        yy = (py - t * sp) % HT; xx = px + 12 * math.sin(t * 0.8 + ph)
        al = int(90 + 80 * math.sin(t * 2 + ph))
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 40, 70, max(0, al)))
    # shake
    sx = sy = 0
    for (st, du) in SHAKES:
        if st <= t < st + du:
            k = 1 - (t - st) / du
            sx = int(math.sin(t * 90) * 16 * k); sy = int(math.cos(t * 77) * 12 * k)
    _CHR.clear()
    _base = [e for e in EL if e['k'] not in UIK]; _ui = [e for e in EL if e['k'] in UIK]
    for ei, e in enumerate(_base + [CAMSENT] + _ui):
        if not (e['t0'] <= t < e['t1']): continue
        k = e['k']
        if k == '__cam__':
            if CAM: fr = apply_cam(fr, t)
            continue
        CUR[0] = (ei, k, e.get('text', '')) if k in ('chip', 'title', 'big', 'sub', 'count', 'days', 'blocks') else None
        if k in ('char', 'squat'):
            dx, dy, s, al = enter_tf(e, t)
            if k == 'squat':
                pose = 'squat'
            else:
                pose = e['pose']
            spr, fx, fy, mk, raw = frame_for(pose, t - e['t0'], e)
            spr = apply_glow(spr, mk, e.get('glow'), t)
            br = 1 + 0.008 * math.sin((t - e['t0']) * 3.2)
            z = 1 + e.get('zoom', 0) * clamp((t - e['t0']) / (e['t1'] - e['t0']))
            sc = e['sc'] * s * z
            cx = e['x'] + dx + sx; cy = e['y'] + dy + sy
            if k == 'char' and e['pose'] == 'run': cy -= abs(math.sin(t * 9)) * 16
            if sc < 0.02: continue
            if e.get('ghost'):
                for gi, off in enumerate((1, 2, 3)):
                    gs = sc * (1 + 0.05 * off * (0.5 + 0.5 * math.sin(t * 4)))
                    gim = spr
                    w_ = int(gim.width * gs); h_ = int(gim.height * gs)
                    gg = gim.resize((w_, h_), Image.BILINEAR)
                    a2 = gg.split()[3].point(lambda v: int(v * 0.16 / off)); gg.putalpha(a2)
                    fr.alpha_composite(gg, (int(cx - fx * gs), int(cy - fy * gs)))
            im = spr
            if e.get('burn'):
                fl = 0.5 + 0.5 * math.sin(t * 18)
                im = spr.copy()
                tint = Image.new('RGBA', im.size, (255, 40, 30, int(70 * fl)))
                tint.putalpha(ImageChops.multiply(im.split()[3], Image.new('L', im.size, int(80 * fl))))
                im = Image.alpha_composite(im, tint)
            w_ = int(im.width * sc * br); h_ = int(im.height * sc * (2 - br))
            if w_ < 2 or h_ < 2: continue
            im2 = im.resize((w_, h_), Image.BILINEAR) if (w_, h_) != im.size else im
            if al < 0.999:
                im2 = im2.copy(); im2.putalpha(im2.split()[3].point(lambda v: int(v * al)))
            # floor shadow
            sh = Image.new('RGBA', (int(300 * sc) + 2, int(40 * sc) + 2), (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, sh.height - 1], fill=(255, 20, 50, int(90 * al)))
            sh = sh.filter(ImageFilter.GaussianBlur(8))
            if pose != 'run':
                fr.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
            fr.alpha_composite(im2, (int(cx - fx * sc * br), int(cy - fy * sc * (2 - br))))
            if AUDIT is not None: AUDIT['chr'].append((im2.split()[3], (int(cx - fx * sc * br), int(cy - fy * sc * (2 - br)))))
            if SUBDODGE: _CHR.append((im2.split()[3], (int(cx - fx * sc * br), int(cy - fy * sc * (2 - br)))))
        elif k == 'loc':
            cur = None; ts0 = e['t0']
            for (tt, nm) in e['seq']:
                if t >= tt: cur = nm; ts0 = tt
            img = LOCS[cur]
            a = t - ts0
            if a < 0.18:
                w = int(WD * out_cubic(a / 0.18))
                fr.alpha_composite(img.crop((0, 0, max(1, w), HT)), (0, 0))
                ImageDraw.Draw(fr).rectangle([w - 8, 0, w + 8, HT], fill=RED + (255,))
            else:
                # slow push-in that settles at +4% and HOLDS (no unbounded growth -> no snap-back at the next scene)
                kz = min(1.0, a / 6.0); z = 1 + 0.04 * kz * kz * (3 - 2 * kz)
                im2 = img.resize((int(WD * z), int(HT * z)), Image.BILINEAR)
                fr.alpha_composite(im2, (-(im2.width - WD) // 2, -(im2.height - HT) // 2))
            fr.alpha_composite(GLOW)
        elif k == 'speed':
            lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            rnd = random.Random(int(t * 15))
            for i in range(46):
                if e['mode'] == 'h':
                    yy = rnd.uniform(60, 1000); x0 = rnd.uniform(-200, WD); L = rnd.uniform(200, 700)
                    dd.line([(x0, yy), (x0 + L, yy)], fill=(255, 60, 80, rnd.randint(40, 120)), width=rnd.randint(2, 6))
                else:
                    ang = rnd.uniform(0, 2 * math.pi); r0 = rnd.uniform(380, 560); r1 = r0 + rnd.uniform(250, 700)
                    cx_, cy_ = 960, 560
                    dd.line([(cx_ + r0 * math.cos(ang), cy_ + r0 * math.sin(ang)), (cx_ + r1 * math.cos(ang), cy_ + r1 * math.sin(ang))], fill=(255, 60, 80, rnd.randint(40, 120)), width=rnd.randint(2, 7))
            fr.alpha_composite(lay)
        elif k == 'burst':
            a = (t - e['t0']) / (e['t1'] - e['t0'])
            lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            for i in range(24):
                ang = i / 24 * 2 * math.pi + a * 0.6
                dd.polygon([(960, 560), (960 + 1400 * math.cos(ang - 0.05), 560 + 1400 * math.sin(ang - 0.05)), (960 + 1400 * math.cos(ang + 0.05), 560 + 1400 * math.sin(ang + 0.05))], fill=(255, 220, 230, int(110 * (1 - a))))
            fr.alpha_composite(lay)
            if a < 0.12: fr.alpha_composite(Image.new('RGBA', (WD, HT), (255, 255, 255, int(200 * (1 - a / 0.12)))))
        elif k == 'fire':
            a = t - e['t0']
            lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            rnd = random.Random(7)
            for i in range(70):
                ph = rnd.uniform(0, 1); sp = rnd.uniform(0.7, 1.4)
                life = (a * sp + ph) % 1
                x0 = e['x'] + rnd.uniform(-230, 150) + 18 * math.sin(a * 6 + i)
                y0 = e['y'] - life * rnd.uniform(160, 300)
                r = (1 - life) * rnd.uniform(14, 30) * min(1, a / 0.3)
                col = (255, int(40 + 120 * (1 - life)), 20, int(170 * (1 - life)))
                dd.ellipse([x0 - r, y0 - r * 1.4, x0 + r, y0 + r], fill=col)
            fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5))); fr.alpha_composite(lay)
        elif k == 'plus':
            a = t - e['t0']
            for i in range(6):
                ph = (a * 0.8 + i / 6) % 1
                xx = e['x'] + (i - 2.5) * 70 + 10 * math.sin(a * 3 + i); yy = e['y'] - ph * 260
                im = cached(('plus',), lambda: text_img('+', font(F_RUSSO, 70), (60, 255, 120, 255), stroke=5, stroke_fill=(0, 60, 20), glow=8, glowcol=(40, 255, 110)))
                paste_scaled(fr, im, xx, yy, 0.6 + 0.5 * (1 - ph), clamp(min(ph / 0.15, (1 - ph) / 0.3)))
        elif k == 'bar':
            a = t - e['t0']; p = out_cubic(clamp(a / 1.6))
            x0, y0 = e['x'], e['y']; W_ = 520
            dd = ImageDraw.Draw(fr)
            dd.rounded_rectangle([x0, y0, x0 + W_, y0 + 46], 14, outline=(255, 255, 255, 255), width=4, fill=(30, 5, 10, 230))
            dd.rounded_rectangle([x0 + 6, y0 + 6, x0 + 6 + (W_ - 12) * p, y0 + 40], 10, fill=(60, 255, 120, 255))
        elif k == 'count':
            a = t - e['t0']; p = clamp(a / 1.9)
            n = int(e['n0'] + (e['n1'] - e['n0']) * (p ** 0.8))
            im = cached(('cnt', n), lambda: text_img(str(n), font(F_RUSSO, 190), (255, 255, 255, 255), stroke=8, stroke_fill=(0, 0, 0), glow=14, glowcol=RED))
            paste_scaled(fr, im, e['x'], e['y'], 1.0 + (0.15 if p >= 1 and a < 2.1 else 0), 1.0)
        elif k == 'bb':
            a = t - e['t0']
            spr = ANIM['flex'][3][0]
            sh = spr.copy(); arr = np.array(sh); arr[..., :3] = (arr[..., :3] * 0.12).astype(np.uint8); sh = Image.fromarray(arr)
            sc_ = 1.35 * out_back(clamp(a / 0.35), 2)
            if sc_ > 0.05:
                w_ = int(sh.width * sc_ * 1.15); h_ = int(sh.height * sc_)
                im2 = sh.resize((w_, h_), Image.BILINEAR)
                fr.alpha_composite(im2, (int(e['x'] - w_ / 2), int(e['y'] - h_ + 60 * sc_)))
        elif k == 'flow':
            a = t - e['t0']
            lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            for j, xo in enumerate((-90, -45, 0, 45, 90)):
                for i in range(9):
                    ph = (a * 0.9 + i / 9 + j * 0.13) % 1
                    yy = e['y'] - 80 - ph * 540; xx = e['x'] + xo + 18 * math.sin(ph * 9 + j)
                    dd.ellipse([xx - 7, yy - 7, xx + 7, yy + 7], fill=(255, 30, 60, int(230 * math.sin(ph * math.pi))))
            fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4))); fr.alpha_composite(lay)
        elif k == 'blocks':
            a = t - e['t0']
            for i in range(5):
                p = clamp((a - i * 0.15) / 0.2)
                x0 = e['x'] + i * 115; y0 = e['y']
                dd = ImageDraw.Draw(fr)
                dd.rounded_rectangle([x0, y0, x0 + 100, y0 + 100], 14, outline=(255, 255, 255, 255), width=4, fill=(RED + (255,)) if p >= 1 else (30, 5, 10, 220))
                if p > 0:
                    im = cached(('blk',), lambda: text_img('10', font(F_RUSSO, 54), (255, 255, 255, 255), stroke=4, stroke_fill=(0, 0, 0)))
                    paste_scaled(fr, im, x0 + 50, y0 + 50, out_back(p, 2), 1.0)
        elif k == 'phone':
            a = t - e['t0']
            paste_scaled(fr, PROPS[6], e['x'], e['y'] + 10 * math.sin(a * 2.5), 0.8 * out_back(clamp(a / 0.3), 2) * (1 + 0.05 * math.sin(a * 6)), 1.0)
        elif k == 'days':
            a = t - e['t0']
            dd = ImageDraw.Draw(fr)
            lab = cached(('dlab', DAY_LABEL), lambda: text_img(DAY_LABEL, font(F_RUSSO, 46), (255, 255, 255, 255), stroke=5, stroke_fill=(0, 0, 0)))
            paste_scaled(fr, lab, e['x'] + 40, e['y'] - 70, 1.0, clamp(a / 0.15))
            for i in range(7):
                col_, row_ = i % 4, i // 4
                x0 = e['x'] + col_ * 120; y0 = e['y'] + row_ * 120
                p = clamp((a - 0.05 - i * 0.1) / 0.12)
                if p <= 0: continue
                s_ = out_back(p, 2)
                w2 = 50 * s_
                cx_, cy_ = x0 + 50, y0 + 50
                dd.rounded_rectangle([cx_ - w2, cy_ - w2, cx_ + w2, cy_ + w2], 14, outline=(255, 255, 255, 255), width=4, fill=RED + (255,))
                num = cached(('dn', i), lambda: text_img(str(i + 1), font(F_RUSSO, 50), (255, 255, 255, 255), stroke=4, stroke_fill=(0, 0, 0)))
                paste_scaled(fr, num, cx_, cy_, s_, 1.0)
        elif k in EXTRA:
            fr = EXTRA[k](fr, e, t) or fr
        elif k == 'prop':
            a = t - e['t0']
            im = PROPS[e['idx']]
            sc_ = e['sc'] * out_back(a / 0.3, 2.2) * (1 + 0.03 * math.sin(a * 3))
            if sc_ > 0.02:
                paste_scaled(fr, im, e['x'] + sx, e['y'] + sy + 6 * math.sin(a * 2.5), sc_, clamp(a / 0.1))
            if e['strike'] and a > 0.45:
                p = clamp((a - 0.45) / 0.2); S = 95
                lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
                cx, cy = e['x'] + sx, e['y'] + sy
                dd.line([(cx - S, cy - S), (cx - S + 2 * S * p, cy - S + 2 * S * p)], fill=RED + (255,), width=16)
                if p >= 1:
                    q = clamp((a - 0.65) / 0.2); dd.line([(cx + S, cy - S), (cx + S - 2 * S * q, cy - S + 2 * S * q)], fill=RED + (255,), width=16)
                fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8))); fr.alpha_composite(lay)
        elif k == 'stairs':
            fr.alpha_composite(stairs_layer(t, e['t0']))
        elif k == 'chip':
            a = t - e['t0']
            im = chip_img(e['text'], e['size'], e['style'])
            s = out_back(a / 0.28, 2.4); al = clamp(a / 0.08)
            b = e['t1'] - t
            if b < 0.12: al *= clamp(b / 0.12)
            if e['style'] == 'check' and t >= 73.28:
                s *= 1 + 0.12 * math.exp(-(t - 73.28) * 5) + 0.03 * math.sin(t * 8)
            if e['style'] == 'dimx' and t >= 73.28:
                al *= 0.45
            ax = 0 if e['anchor'] == 'l' else 0.5
            x = e['x'] + sx; y = e['y'] + sy
            paste_scaled(fr, im, x + (im.width * (0.5 - ax)) * (1 - s) * 0, y, s, al, ax=ax, ay=0.5)
            if e['style'] == 'strike':
                p = clamp((a - 0.45) / 0.25)
                draw_strike(fr, x + 22, y - im.height / 2 + 22, im.width - 44, im.height - 44, p)
        elif k == 'title':
            a = t - e['t0']
            txt = e['text']
            n = len(txt) if not e['type'] else min(len(txt), int(a / 0.035) + 1)
            f = font(F_RUSSO, e['size'])
            im = cached(('t', txt[:n], e['size'], e['col']), lambda: text_img(txt[:n], f, e['col'] + (255,), stroke=3, stroke_fill=(20, 0, 5), glow=14))
            al = 1.0; b = e['t1'] - t
            if b < 0.12: al = clamp(b / 0.12)
            full = cached(('tw', txt, e['size']), lambda: text_img(txt, f, (255, 255, 255, 255), stroke=3, glow=14).width)
            if e['anchor'] == 'c':
                x0 = e['x'] - full / 2
            else:
                x0 = e['x']
            paste_scaled(fr, im, x0 + sx, e['y'] + sy, 1, al, ax=0, ay=0.5)
            if e['type'] and n < len(txt) and int(t * 6) % 2 == 0:
                ImageDraw.Draw(fr).rectangle([x0 + im.width - 10, e['y'] - e['size'] * 0.4, x0 + im.width - 4, e['y'] + e['size'] * 0.4], fill=RED)
        elif k == 'big':
            a = t - e['t0']; b = e['t1'] - t
            f = font(F_RUSSO, e['size'])
            im = cached(('big', e['text'], e['size']), lambda: text_img(e['text'], f, (255, 255, 255, 255), stroke=5, stroke_fill=RED, glow=30))
            s = 1.6 - 0.6 * out_cubic(a / 0.18); al = clamp(a / 0.08)
            if b < 0.15: al *= clamp(b / 0.15); s *= 1 + (0.15 - b)
            # glitch: rgb offset for first 0.15s
            if a < 0.2 and int(a * 60) % 3 == 0:
                paste_scaled(fr, im, e['x'] + 14, e['y'] + sy, s, al * 0.5)
            paste_scaled(fr, im, e['x'] + sx, e['y'] + sy, s, al)
        elif k == 'x':
            a = t - e['t0']
            lay = Image.new('RGBA', (WD, HT), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            cx, cy, S = e['cx'] + sx, e['cy'] + sy, e['s']
            p1 = clamp(a / 0.18); p2 = clamp((a - 0.2) / 0.18)
            if p1 > 0: dd.line([(cx - S, cy - S), (cx - S + 2 * S * p1, cy - S + 2 * S * p1)], fill=RED + (255,), width=34)
            if p2 > 0: dd.line([(cx + S, cy - S), (cx + S - 2 * S * p2, cy - S + 2 * S * p2)], fill=RED + (255,), width=34)
            fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14))); fr.alpha_composite(lay)
        elif k == 'sub':
            a = t - e['t0']
            lab = SUB_LABELS[0] if int(a / 1.1) % 2 == 0 else SUB_LABELS[1]
            im = chip_img(lab, 40, 'on')
            # box is at chest of 'box' pose; compute position
            spr, fx, fy = SPR['box']; sc = 1.1
            dx, dy, s, al = enter_tf(dict(t0=e['t0'], t1=e['t1'], enter='up'), t)
            bx = 1430; by = 470 + dy
            pulse_s = 1 + 0.06 * math.sin(a * 7)
            paste_scaled(fr, im, bx, by, pulse_s)
            # cursor click
            ph = (a % 1.1) / 1.1
            cxp, cyp = bx + 60 - 40 * out_cubic(ph / 0.3), by + 40 - 20 * out_cubic(ph / 0.3)
            dd = ImageDraw.Draw(fr)
            dd.polygon([(cxp, cyp), (cxp, cyp + 44), (cxp + 12, cyp + 33), (cxp + 22, cyp + 52), (cxp + 30, cyp + 48), (cxp + 20, cyp + 30), (cxp + 36, cyp + 30)], fill=(255, 255, 255), outline=(0, 0, 0))
    # subtitles
    CUR[0] = ('SUB', 'sub', '')
    for (s0, s1, c) in SUBS:
        if s0 <= t < s1:
            f = font(F_M900, 52)
            words = [w for w, _, _ in c]
            act = 0
            for i, (w, a, b) in enumerate(c):
                if t >= a: act = i
            # layout
            sp = f.getlength(' ')
            ws = [f.getlength(w.upper()) for w in words]
            tot = sum(ws) + sp * (len(ws) - 1)
            x = WD / 2 - tot / 2; y = sub_y(t, tot)
            pop = out_back((t - c[act][1]) / 0.15, 3)
            for i, w in enumerate(words):
                up = w.upper()
                isnum = any(ch.isdigit() for ch in w)
                col = RED2 if (i == act or isnum) else (255, 255, 255)
                im = cached(('sw', up, col), lambda: text_img(up, f, col + (255,), stroke=6, stroke_fill=(0, 0, 0), glow=0))
                sc = (1 + 0.12 * (1 - pop) * 0 + 0.0) if i != act else 0.9 + 0.1 * pop
                paste_scaled(fr, im, x + ws[i] / 2, y, sc, 1.0)
                x += ws[i] + sp
            break
    # scanlines + slight chromatic vibe: thin dark lines
    # fade in/out
    if t < 0.25 or t > DUR - 0.6:
        k2 = clamp(t / 0.25) if t < 0.25 else clamp((DUR - t) / 0.6)
        black = Image.new('RGBA', (WD, HT), (0, 0, 0, int(255 * (1 - k2))))
        fr.alpha_composite(black)
    for pt in PUNCH:
        if pt <= t < pt + 0.3:
            k3 = 1 - (t - pt) / 0.3; z = 1 + 0.045 * k3 * k3
            big_ = fr.resize((int(WD * z), int(HT * z)), Image.BILINEAR)
            fr = big_.crop(((big_.width - WD) // 2, (big_.height - HT) // 2, (big_.width - WD) // 2 + WD, (big_.height - HT) // 2 + HT))
            break
    return fr.convert('RGB').tobytes()

def init():
    global BG, GLOW
    for n in ('home', 'park', 'office', 'roof'):
        im = Image.open(f'/home/claude/p2d/bg/{n}.png').convert('RGB').resize((WD, HT), Image.LANCZOS)
        a = np.array(im).astype(np.float32) * 0.5; a[..., 0] = a[..., 0] * 1.12 + 10; a[..., 2] *= 0.88
        LOCS[n] = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    load_sprites(); BG = make_bg(); GLOW = make_glow()

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'full'
    if mode == 'still':
        init()
        for ts in sys.argv[2:]:
            t = float(ts); b = render(int(t * FPS))
            Image.frombytes('RGB', (WD, HT), b).save(f'/home/claude/work/still_{ts}.png')
        sys.exit()
    n = int(DUR * FPS)
    start = int(float(sys.argv[2]) * FPS) if len(sys.argv) > 2 else 0
    end = int(float(sys.argv[3]) * FPS) if len(sys.argv) > 3 else n
    out = sys.argv[4] if len(sys.argv) > 4 else '/home/claude/work/video_noaudio.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WD}x{HT}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    with Pool(2, initializer=init) as p:
        for i, b in enumerate(p.imap(render, range(start, end), chunksize=8)):
            ff.stdin.write(b)
            if i % 300 == 0: print(i, flush=True)
    ff.stdin.close(); ff.wait()
