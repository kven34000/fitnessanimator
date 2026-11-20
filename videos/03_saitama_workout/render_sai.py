import sys, os, json, math, subprocess
sys.path.insert(0, '/home/claude/work'); sys.path.insert(0, '/home/claude/v3_sai')
import numpy as np
from PIL import Image
import render_v2 as R
from script_en import SEG, DUR

R.DUR = DUR
R.SUBDODGE = False
R.CAM_FLOOR = 995
R.CAM_MAXZ = 1.15
R.SUB_LABELS = ('SUBSCRIBE', 'LIKE'); R.DAY_LABEL = 'DAY'
SPRDIR = R.SPRDIR

# ---------------- new sheets ----------------
# name: (rows, cols, scale-mode, target)
NEW = dict(situp=(4, 4, 'w', 900), plank=(4, 2, 'w', 1050), sore=(2, 4, 'h', 780), hair=(2, 4, 'h', 780), hero=(2, 4, 'h', 800), legraise=(1, 1, 'w', 1000), tablerow=(4, 2, 'h', 620), pullup=(2, 4, 'h', 760), dips=(2, 4, 'h', 760), decline=(4, 2, 'w', 1050), pushup=(4, 2, 'w', 1050),
           bulgarian=(2, 4, 'h', 740), rdl=(2, 4, 'h', 740), benchdip=(2, 4, 'h', 700), pain=(2, 4, 'h', 760),
           row=(2, 2, 'w', 1000), fatrobe=(2, 4, 'h', 760), fatbar=(2, 4, 'h', 820), lab=(2, 4, 'h', 780),
           wheel=(2, 4, 'h', 640), heavysquat=(2, 4, 'h', 760), latpull=(2, 4, 'h', 820), shoulder=(2, 4, 'h', 770),
           fingers=(2, 4, 'h', 780), stop=(2, 4, 'h', 780), pray=(2, 4, 'h', 780), tired=(2, 4, 'h', 640),
           notepad=(2, 4, 'h', 560), lazy=(4, 2, 'w', 1000), weightdip=(2, 4, 'h', 780),
           rowbar=(2, 4, 'h', 820), sidepull=(2, 4, 'h', 880), benchpress=(2, 4, 'w', 900), facepalm=(2, 4, 'h', 780),
           tools=(2, 4, 'h', 780), stretch=(2, 4, 'h', 820), thumbs2=(2, 4, 'h', 780), dumbbell=(2, 4, 'h', 780))
STATIC_SCALE = dict(pullup=0.95, fatbar=0.9)
SHEETDIM = dict(row=(2400, 880))
SHEET_W, SHEET_H = 2400, 1792
PERIOD = dict(situp=2.4, plank=4.0, sore=4.0, hair=4.0, hero=4.0, legraise=3.0, tablerow=3.6, rowbar=2.4, sidepull=4.0, benchpress=3.0, facepalm=3.2, tools=4.0, stretch=4.0, thumbs2=3.2, dumbbell=2.6, fatrobe=4.0, fatbar=3.2, lab=4.0, wheel=4.0, heavysquat=2.6, latpull=2.4, shoulder=3.6, fingers=4.0, stop=3.2, pray=4.0, tired=3.2, notepad=4.0, lazy=4.0, weightdip=3.2, pullup=2.4, dips=3.2, decline=3.0, pushup=1.6, bulgarian=2.4, rdl=2.8, benchdip=1.8, pain=3.2, row=2.0)

_orig_load = R.load_sprites
def load_sprites():
    _orig_load()
    for nm, (rows, cols, mode, tgt) in NEW.items():
        d = f'{SPRDIR}/{nm}'
        if os.path.exists(f'{SPRDIR}/{nm}S/info.json'):
            dS = f'{SPRDIR}/{nm}S'; info = json.load(open(f'{dS}/info.json')); cwS, chS = info['canvas']
            sc = tgt / (chS if mode == 'h' else cwS) * STATIC_SCALE.get(nm, 1.0)
            frs = []
            for i in range(info['n']):
                im = Image.open(f'{dS}/f{i}.png').convert('RGBA')
                mk = Image.open(f'{dS}/f{i}_m.png').convert('RGBA') if os.path.exists(f'{dS}/f{i}_m.png') else None
                sz = (max(1, int(im.width * sc)), max(1, int(im.height * sc)))
                im2 = im.resize(sz, Image.LANCZOS)
                mk2 = Image.merge('RGBA', [c.resize(sz, Image.BILINEAR) for c in mk.split()]) if mk is not None else None
                big, fx, fy, mb, raw = R._mk(im2, mk2)
                frs.append((big, sz[0] / 2 + 60, sz[1] + 60 - 4, mb, raw))
            R.ANIM[nm] = frs; R.SPR[nm] = frs[0][:3]
            continue
        if not os.path.exists(f'{d}/fboxes.json'): continue
        boxes = json.load(open(f'{d}/fboxes.json'))
        ims = [Image.open(f'{d}/f{i}.png').convert('RGBA') for i in range(len(boxes))]
        mks = [Image.open(f'{d}/f{i}_m.png').convert('RGBA') if os.path.exists(f'{d}/f{i}_m.png') else None for i in range(len(boxes))]
        if mode == 'h': ref = sorted(i.height for i in ims)[len(ims) // 2]
        else: ref = sorted(i.width for i in ims)[len(ims) // 2]
        sc = tgt / ref
        sw, sh_ = SHEETDIM.get(nm, (SHEET_W, SHEET_H))
        cw, chh = sw / cols, sh_ / rows
        # anchor: fixed point of each cell (cell centre x, cell bottom y), shifted to typical feet line
        offs = []
        for (x0, y0, x1, y1) in boxes:
            r = int(((y0 + y1) / 2) // chh); offs.append((r + 1) * chh - y1)
        off = sorted(offs)[len(offs) // 2]
        frs = []
        for im, mk, (x0, y0, x1, y1) in zip(ims, mks, boxes):
            r = int(((y0 + y1) / 2) // chh); c = int(((x0 + x1) / 2) // cw)
            ax = (c + 0.5) * cw - x0; ay = (r + 1) * chh - off - y0
            sz = (max(1, int(im.width * sc)), max(1, int(im.height * sc)))
            im2 = im.resize(sz, Image.LANCZOS)
            mk2 = Image.merge('RGBA', [ch.resize(sz, Image.BILINEAR) for ch in mk.split()]) if mk is not None else None
            big, fx, fy, mb, raw = R._mk(im2, mk2)
            frs.append((big, ax * sc + 60, ay * sc + 60, mb, raw))
        frs = register(nm, frs)
        R.ANIM[nm] = frs
        R.SPR[nm] = frs[0][:3]
R.load_sprites = load_sprites

REG = dict(pullup='top', fatbar='top', sidepull='bottom', latpull='all', rowbar='bottom', row='bottom')
def register(nm, frs, q=4):
    # align every frame to frame 0 by correlating a stable band (feet/equipment) of the alpha masks
    from scipy.signal import fftconvolve
    mode = REG.get(nm, 'bottom')
    Wc = max(f[0].width for f in frs) * 4; Hc = max(f[0].height for f in frs) * 4
    Cx, Cy = Wc // 2, Hc // 2
    def canvas(f, dx=0, dy=0):
        c = np.zeros((Hc // q, Wc // q), np.float32)
        a = np.asarray(f[0].split()[3].resize((f[0].width // q, f[0].height // q)), np.float32) / 255
        a = (a > 0.6).astype(np.float32)
        x0 = int((Cx - f[1]) / q + dx); y0 = int((Cy - f[2]) / q + dy)
        H_, W_ = c.shape; ys0, xs0 = max(0, -y0), max(0, -x0)
        ye, xe = min(a.shape[0], H_ - y0), min(a.shape[1], W_ - x0)
        if ye > ys0 and xe > xs0: c[y0 + ys0:y0 + ye, x0 + xs0:x0 + xe] = a[ys0:ye, xs0:xe]
        return c
    def band(c):
        ys = np.nonzero(c.sum(1))[0]
        if not len(ys): return c
        top, bot = ys[0], ys[-1]; h = bot - top; m = np.zeros_like(c)
        if mode == 'bottom': m[bot - int(h * 0.16):bot + 1] = 1
        elif mode == 'top': m[top:top + int(h * 0.10)] = 1
        else: m[:] = 1
        return c * m
    ref = band(canvas(frs[0])); out = [frs[0]]
    R_ = 60
    for f in frs[1:]:
        c = band(canvas(f))
        cor = fftconvolve(ref, c[::-1, ::-1], mode='same')
        cy, cx = np.array(cor.shape) // 2
        win = cor[cy - R_:cy + R_, cx - R_:cx + R_]
        iy, ix = np.unravel_index(np.argmax(win), win.shape)
        dy, dx = iy - R_, ix - R_
        out.append((f[0], f[1] - dx * q, f[2] - dy * q, f[3], f[4]))
    return out

_orig_ff = R.frame_for
def frame_for(pose, a, e):
    if e.get('frames'):
        frs = R.ANIM[pose]; fl = e['frames']; k = int(a / 0.6) % (2 * len(fl))
        return frs[fl[k if k < len(fl) else 2 * len(fl) - 1 - k]]
    if e.get('keys'):
        frs = R.ANIM[pose]; ks = e['keys']; L = e.get('loop')
        a2 = a % L if L else a
        return frs[int(round(float(np.interp(a2, [k[0] for k in ks], [k[1] for k in ks])))) % len(frs)]
    if pose in NEW:
        frs = R.ANIM[pose]; P = e.get('period') or PERIOD[pose]
        return frs[int((a % P) / P * len(frs)) % len(frs)]
    return _orig_ff(pose, a, e)
R.frame_for = frame_for

_orig_glow = R.apply_glow
def apply_glow(spr, mk, glow, t):
    if not glow: return spr
    cols = {g[2] for g in glow if len(g) > 2}
    if not cols: return _orig_glow(spr, mk, glow, t)
    old = R.GLOWC; R.GLOWC = list(cols)[0]
    try: return _orig_glow(spr, mk, [g[:2] for g in glow], t)
    finally: R.GLOWC = old
R.apply_glow = apply_glow

# ---------------- extra drawers ----------------
from PIL import ImageDraw, ImageFilter
_cache = {}
def _inset_img(e, t):
    key = (e['pose'], e['fr'], e['box'], e['chans'], e['r'], e['col'])
    if key in _cache: return _cache[key]
    big, fx_, fy_, mk, raw = R.ANIM[e['pose']][e['fr']]
    im = big
    if e['chans'] and mk is not None:
        g = [(c, -10.0) + ((e['col'],) if e['col'] else ()) for c in e['chans']]
        im = apply_glow(big, mk, g, 0.0)
    W_, H_ = im.size; x0, y0, x1, y1 = e['box']
    cx, cy = (x0 + x1) / 2 * W_, (y0 + y1) / 2 * H_; side = max((x1 - x0) * W_, (y1 - y0) * H_)
    crop = im.crop((int(cx - side / 2), int(cy - side / 2), int(cx + side / 2), int(cy + side / 2)))
    r = e['r']; D = 2 * r
    bg = Image.new('RGBA', (D, D), (25, 4, 10, 255)); bg.alpha_composite(crop.resize((D, D), Image.LANCZOS))
    m = Image.new('L', (D, D), 0); ImageDraw.Draw(m).ellipse([0, 0, D - 1, D - 1], fill=255)
    out = Image.new('RGBA', (D + 60, D + 60), (0, 0, 0, 0))
    ring = Image.new('RGBA', out.size, (0, 0, 0, 0))
    col = e['col'] or (40, 255, 110) if e['chans'] else R.RED
    ImageDraw.Draw(ring).ellipse([24, 24, D + 36, D + 36], outline=col + (255,), width=10)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(10)))
    bg.putalpha(m); out.alpha_composite(bg, (30, 30))
    ImageDraw.Draw(out).ellipse([28, 28, D + 32, D + 32], outline=(255, 255, 255, 255), width=5)
    _cache[key] = out; return out
def draw_inset(fr, e, t):
    a = t - e['t0']; s = R.out_back(R.clamp(a / 0.3), 2.2)
    if s <= 0.02: return fr
    im = _inset_img(e, t)
    R.paste_scaled(fr, im, e['x'], e['y'] + 6 * math.sin(a * 2 + e['x']), s)
    if e.get('label'):
        R.CUR[0] = ('inset', 'inset', e['label'])
        lab = R.chip_img(e['label'], 34, 'on')
        R.paste_scaled(fr, lab, e['x'], e['y'] + e['r'] + 40, s)
        R.CUR[0] = None
    return fr
def draw_card(fr, e, t):
    a = t - e['t0']; s = R.out_back(R.clamp(a / 0.3), 2)
    key = ('card', tuple(e['lines']))
    if key not in _cache:
        f1 = R.font(R.F_RUSSO, 92); f2 = R.font(R.F_M900, 56)
        W_, H_ = 760, 460
        im = Image.new('RGBA', (W_ + 60, H_ + 60), (0, 0, 0, 0))
        gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle([30, 30, W_ + 30, H_ + 30], 36, outline=R.RED + (255,), width=12)
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))
        d = ImageDraw.Draw(im); d.rounded_rectangle([30, 30, W_ + 30, H_ + 30], 36, fill=(30, 5, 12, 240), outline=R.RED + (255,), width=6)
        y = 80
        for i, ln in enumerate(e['lines']):
            f = f1 if i == 0 else f2; bb = f.getbbox(ln)
            d.text((30 + (W_ - (bb[2] - bb[0])) / 2 - bb[0], y), ln, font=f, fill=(255, 255, 255) if i else R.RED2)
            y += (bb[3] - bb[1]) + 50
        _cache[key] = im
    R.CUR[0] = ('card', 'card', e['lines'][0])
    R.paste_scaled(fr, _cache[key], e['x'], e['y'], s); R.CUR[0] = None
    return fr
def draw_bubble(fr, e, t):
    a = t - e['t0']; s = R.out_back(R.clamp(a / 0.25), 2.4)
    key = ('bub', e['text'])
    if key not in _cache:
        f = R.font(R.F_RUSSO, 66); bb = f.getbbox(e['text'])
        px, py = 72, 46; tw, th = bb[2] - bb[0], bb[3] - bb[1]
        w, h = tw + 2 * px, th + 2 * py
        im = Image.new('RGBA', (w + 120, h + 120), (0, 0, 0, 0))
        gl = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle([40, 20, 40 + w, 20 + h], 26, outline=R.RED + (255,), width=10)
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([40, 20, 40 + w, 20 + h], 26, fill=(255, 255, 255, 250), outline=R.RED + (255,), width=6)
        for (cx, cy, rr) in ((52, h + 46, 15), (28, h + 78, 9)):
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(255, 255, 255, 250), outline=R.RED + (255,), width=4)
        d.text((40 + px - bb[0], 20 + py - bb[1]), e['text'], font=f, fill=(20, 0, 5))
        _cache[key] = im
    R.CUR[0] = ('bubble', 'bubble', e['text'])
    R.paste_scaled(fr, _cache[key], e['x'], e['y'] + 8 * math.sin(a * 3), s); R.CUR[0] = None
    return fr
def draw_calendar(fr, e, t):
    a = t - e['t0']; s = R.out_back(R.clamp(a / 0.35), 2)
    key = ('cal', e['text'])
    if key not in _cache:
        W_, H_ = 420, 440
        im = Image.new('RGBA', (W_ + 60, H_ + 60), (0, 0, 0, 0))
        gl = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle([30, 30, W_ + 30, H_ + 30], 30, outline=R.RED + (255,), width=12)
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([30, 30, W_ + 30, H_ + 30], 30, fill=(245, 240, 240, 255), outline=R.RED + (255,), width=6)
        d.rounded_rectangle([30, 30, W_ + 30, 140], 30, fill=R.RED + (255,)); d.rectangle([30, 100, W_ + 30, 140], fill=R.RED + (255,))
        for k in range(4):
            x = 90 + k * 100; d.rounded_rectangle([x - 8, 10, x + 8, 60], 6, fill=(60, 60, 60, 255))
        n, word = e['text'].split(' ', 1)
        f1 = R.font(R.F_RUSSO, 200); f2 = R.font(R.F_M900, 56)
        bb = f1.getbbox(n); d.text((30 + (W_ - (bb[2] - bb[0])) / 2 - bb[0], 165 - bb[1]), n, font=f1, fill=(30, 5, 10))
        bb = f2.getbbox(word); d.text((30 + (W_ - (bb[2] - bb[0])) / 2 - bb[0], 400 - bb[1]), word, font=f2, fill=R.RED)
        _cache[key] = im
    R.CUR[0] = ('calendar', 'calendar', e['text'])
    R.paste_scaled(fr, _cache[key], e['x'], e['y'], s); R.CUR[0] = None
    return fr
def _glowline(fr, pts, col, w, p=1.0, head=True):
    from PIL import ImageDraw, ImageFilter
    n = max(2, int(len(pts) * p)); pts = pts[:n]
    lay = Image.new('RGBA', (R.WD, R.HT), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=col + (255,), width=w + 10, joint='curve')
    lay = lay.filter(ImageFilter.GaussianBlur(9)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=(255, 255, 255, 255), width=w, joint='curve')
    if head and len(pts) > 2:
        (x1, y1), (x0, y0) = pts[-1], pts[-3]; ang = math.atan2(y1 - y0, x1 - x0); L = w * 3.2
        tri = [(x1 + math.cos(ang) * L * 0.4, y1 + math.sin(ang) * L * 0.4),
               (x1 + math.cos(ang + 2.5) * L, y1 + math.sin(ang + 2.5) * L), (x1 + math.cos(ang - 2.5) * L, y1 + math.sin(ang - 2.5) * L)]
        d.polygon(tri, fill=(255, 255, 255, 255))
    fr.alpha_composite(lay)
def draw_arrow(fr, e, t):
    a = t - e['t0']; p = R.out_cubic(R.clamp(a / e.get('dur', 0.45)))
    x0, y0, x1, y1 = e['p']; bend = e.get('bend', 0.0)
    mx, my = (x0 + x1) / 2 - (y1 - y0) * bend, (y0 + y1) / 2 + (x1 - x0) * bend
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1) for u in np.linspace(0, 1, 40)]
    if e.get('loop'):
        p = ((a % e['loop']) / e['loop']) * 1.4; p = min(1, p)
    _glowline(fr, pts, e.get('col', R.RED), e.get('w', 10), p)
    return fr
def draw_ring(fr, e, t):
    from PIL import ImageDraw, ImageFilter
    a = t - e['t0']; s = R.out_back(R.clamp(a / 0.3), 2.5); r = e['r'] * s * (1 + 0.06 * math.sin(a * 6))
    col = e.get('col', (255, 215, 40))
    lay = Image.new('RGBA', (R.WD, R.HT), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x, y = e['x'], e['y']
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (40,), outline=col + (255,), width=9)
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6))); fr.alpha_composite(lay)
    return fr
def draw_measure(fr, e, t):
    a = t - e['t0']; p = R.out_cubic(R.clamp(a / 0.5))
    x, y0, y1 = e['x'], e['y0'], e['y1']; ym = y1 + (y0 - y1) * p
    _glowline(fr, [(x, y1), (x, ym)], R.RED, 8, 1.0, head=False)
    _glowline(fr, [(x - 30, y1), (x + 30, y1)], R.RED, 8, 1.0, head=False)
    if p > 0.95: _glowline(fr, [(x - 30, y0), (x + 30, y0)], R.RED, 8, 1.0, head=False)
    lab = R.chip_img(e['text'], 40, 'on'); R.CUR[0] = ('measure', 'measure', e['text'])
    R.paste_scaled(fr, lab, x - 40 if e.get('left') else x + 40, (y0 + y1) / 2, p, ax=1 if e.get('left') else 0); R.CUR[0] = None
    return fr
def draw_countdown(fr, e, t):
    a = t - e['t0']; d = e['t1'] - e['t0']; n0, n1 = e['n0'], e['n1']
    n = int(math.ceil(n0 - (n0 - n1) * a / d)) if n0 > n1 else int(n0 + (n1 - n0) * a / d)
    n = max(min(n0, n1), min(max(n0, n1), n))
    im = R.cached(('cd', n, e.get('size', 200)), lambda: R.text_img(str(n) + e.get('suf', ''), R.font(R.F_RUSSO, e.get('size', 200)), (255, 255, 255, 255), stroke=10, stroke_fill=(0, 0, 0), glow=16, glowcol=R.RED))
    ph = (a * abs(n0 - n1) / d) % 1; s = 1 + 0.18 * max(0, 1 - ph * 4)
    R.CUR[0] = ('countdown', 'countdown', str(n)); R.paste_scaled(fr, im, e['x'], e['y'], s); R.CUR[0] = None
    return fr
R.EXTRA.update(inset=draw_inset, card=draw_card, bubble=draw_bubble, calendar=draw_calendar, arrow=draw_arrow, ring=draw_ring, measure=draw_measure, countdown=draw_countdown)

exec(open('/home/claude/v3_sai/timeline_sai.py').read())
if os.environ.get('NOHERO'): R.EL[:] = [e for e in R.EL if not (e['k'] == 'char' and e.get('pose') == 'hero')]

# ---------------- subtitles (estimated word timing until the voice is recorded) ----------------
def build_subs(segs, dur):
    W = []
    for i, (t0, s) in enumerate(segs):
        t1 = segs[i + 1][0] if i + 1 < len(segs) else dur
        words = s.split(); wts = [len(w) + 2 for w in words]; tot = sum(wts)
        span = (t1 - t0) * 0.92; c = t0
        for w, wt in zip(words, wts):
            d = span * wt / tot; W.append((w, c, c + d * 0.9)); c += d
    chunks = []; cur = []
    for i, (w, a, b) in enumerate(W):
        cur.append((w, a, b)); txt = ' '.join(x[0] for x in cur)
        nxt = W[i + 1] if i + 1 < len(W) else None
        if w[-1] in '.,?!:' or len(cur) >= 4 or len(txt) > 22 or (nxt and nxt[1] - b > 0.3) or nxt is None:
            chunks.append(cur); cur = []
    out = []
    for j, c in enumerate(chunks):
        s = c[0][1]; e = chunks[j + 1][0][1] if j + 1 < len(chunks) else c[-1][2] + 0.6
        out.append((s, min(e, c[-1][2] + 0.6), c))
    return out
# ---------------- remap the timeline onto the recorded voice ----------------
VA = None
if os.path.exists('/home/claude/v3_sai/vo_align.py'):
    import vo_align as VA
if VA is not None and VA.__dict__.get('TM'):
    TMf = VA.TM
    for e in R.EL:
        e['t0'] = TMf(e['t0']); e['t1'] = TMf(e['t1']) if e['t1'] < 1e8 else e['t1']
        if e.get('glow'): e['glow'] = [(g[0], TMf(g[1])) + tuple(g[2:]) for g in e['glow']]
        if e.get('seq'): e['seq'] = [(TMf(a),) + tuple(r) for (a, *r) in e['seq']]
    R.CAM[:] = [(TMf(c[0]), TMf(c[1])) + tuple(c[2:]) for c in R.CAM]
    R.SHAKES[:] = [(TMf(a), d) for (a, d) in R.SHAKES]
    R.PUNCH[:] = [TMf(p) for p in R.PUNCH]
    DUR = VA.NEW_DUR; R.DUR = DUR
    # glue consecutive scenes of the same sprite at the same place: no pop-out / pop-in between them
    chars = [e for e in R.EL if e['k'] == 'char']
    for a in chars:
        for b in chars:
            if b is not a and b['pose'] == a['pose'] and abs(b['t0'] - a['t1']) < 0.06 and abs(b['x'] - a['x']) < 2 and abs(b['y'] - a['y']) < 2 and abs(b['sc'] - a['sc']) < 0.01:
                a['exit'] = 'none'; b['enter'] = 'none'
def subs_from_words(W):
    chunks = []; cur = []
    for i, (w, a, b) in enumerate(W):
        cur.append((w, a, b)); txt = ' '.join(x[0] for x in cur)
        nxt = W[i + 1] if i + 1 < len(W) else None
        if w[-1] in '.,?!:' or len(cur) >= 4 or len(txt) > 22 or (nxt and nxt[1] - b > 0.3) or nxt is None:
            chunks.append(cur); cur = []
    out = []
    for j, c in enumerate(chunks):
        s = c[0][1]; e = chunks[j + 1][0][1] if j + 1 < len(chunks) else c[-1][2] + 0.6
        out.append((s, min(e, c[-1][2] + 0.6), c))
    return out
R.SUBS[:] = subs_from_words(VA.WORDS) if VA is not None else build_subs(SEG, DUR)
_chars = [e for e in R.EL if e['k'] == 'char']
for _a in _chars:
    for _b in _chars:
        if _b is not _a and _b['pose'] == _a['pose'] and abs(_b['t0'] - _a['t1']) < 0.06 and abs(_b['x'] - _a['x']) < 2 and abs(_b['y'] - _a['y']) < 2 and abs(_b['sc'] - _a['sc']) < 0.01:
            _a['exit'] = 'none'; _b['enter'] = 'none'
sync_text([w for sw in R.SUBS for w in sw[2]])

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        R.init()
        for ts in sys.argv[2:]:
            Image.frombytes('RGB', (R.WD, R.HT), R.render(int(float(ts) * R.FPS))).save(f'/home/claude/v3_sai/still_{ts}.png')
        sys.exit()
    out = sys.argv[2]
    start = float(sys.argv[3]) if len(sys.argv) > 3 else 0; end = float(sys.argv[4]) if len(sys.argv) > 4 else DUR
    from multiprocessing import Pool
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{R.WD}x{R.HT}', '-r', str(R.FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    with Pool(2, initializer=R.init, maxtasksperchild=None) as p:
        for i, b in enumerate(p.imap(R.render, range(int(start * R.FPS), int(end * R.FPS)), chunksize=8)):
            ff.stdin.write(b)
            if i % 900 == 0: print(i, flush=True)
    ff.stdin.close(); ff.wait()
