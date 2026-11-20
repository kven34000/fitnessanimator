"""side jump pull-up: one fixed station (plate cell 4), person from _noeq aligned so grip lies on the bar."""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
D = '/home/claude/p2d'
O = np.asarray(Image.open(f'{D}/sheets/sidepull.png').convert('RGB')).astype(np.float32)
N = np.asarray(Image.open(f'{D}/sheets/sidepull_noeq.png').convert('RGB')).astype(np.float32)
PL = np.asarray(Image.open(f'{D}/sheets/sidepull_plate.png').convert('RGB')).astype(np.float32)
CH, CW = 896, 600
def cell(a, k): r, c = divmod(k, 4); return a[r*CH:(r+1)*CH, c*CW:(c+1)*CW]
def key(a): return 1 - np.clip((a[..., 1] - np.maximum(a[..., 0], a[..., 2]) - 25) / 65, 0, 1)
def despill(a):
    a = a.copy(); mx = np.maximum(a[..., 0], a[..., 2]); a[..., 1] = np.minimum(a[..., 1], mx + 8); return a
def clean(m, mn):
    lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > mn])
PC = 4
pa = key(cell(PL, PC)); pa = pa * clean(pa > 0.5, 2000); prgb = cell(despill(PL), PC)
pd = pa > 0.5
# plate bar: horizontal part between posts -> fit line of top edge
xs_bar = np.arange(110, 420)
tops = np.array([np.nonzero(pd[:300, x])[0].min() for x in xs_bar])
pb = np.polyfit(xs_bar, tops, 1)
bar_top = lambda x: np.polyval(pb, x)
BAR_T = 14  # thickness
FLOOR = 870
def orig_bar(k, per):
    so = cell(O, k); eq = (so.max(2) < 90) & ~per
    cnt = eq[:, 150:420].sum(1); rows = np.nonzero(cnt > 40)[0]
    if len(rows) == 0: return None
    ys, xs = np.nonzero(eq[rows.min():rows.max() + 1, 120:430]); ys += rows.min(); xs += 120
    # top edge per x
    t = {}
    for y, x in zip(ys, xs): t[x] = min(t.get(x, 9999), y)
    X = np.array(sorted(t)); Y = np.array([t[x] for x in X])
    return np.polyfit(X, Y, 1)
PAD = 120
shape = (CH + 2 * PAD, CW + 2 * PAD)
def put(sub, dy, dx=0):
    o = np.zeros(shape + sub.shape[2:], sub.dtype); o[PAD+dy:PAD+dy+sub.shape[0], PAD+dx:PAD+dx+sub.shape[1]] = sub; return o
Pa, Prgb = put(pa, 0), put(prgb, 0)
use = [0, 1, 2, 3, 4, 5, 6, 7]
frames = []
for k in use:
    na = key(cell(N, k)); na = na * ndi.binary_dilation(clean(na > 0.5, 1500), iterations=4); per = na > 0.5
    ys, xs = np.nonzero(per)
    grip_x = None
    if k in (0, 7):
        dy = FLOOR - ys.max()
    elif k == 1:
        top = ys.min(); hx = xs[ys < top + 15].mean()
        dy = int(round(bar_top(hx) + 4 - top)); grip_x = hx
    else:
        ob = orig_bar(k, per)
        # grip x = person pixels around the original bar line
        yb = np.polyval(ob, xs); near = np.abs(ys - (yb + 7)) < 14
        hx = xs[near]; grip_x = np.median(hx)
        dy = int(round(bar_top(grip_x) - np.polyval(ob, grip_x)))
    Na, Nrgb = put(na, dy), put(cell(despill(N), k), dy)
    A = np.clip(Na + Pa * (1 - Na), 0, 1)
    rgb = (Nrgb * Na[..., None] + Prgb * (Pa * (1 - Na))[..., None]) / np.maximum(A, 1e-4)[..., None]
    if grip_x is not None and k != 1:
        # bar in front of the fists (within +-45px of the grip)
        yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
        band = (np.abs(xx - PAD - grip_x) < 45) & (Pa > 0.5) & (yy - PAD < bar_top(xx - PAD) + BAR_T + 6) & (yy - PAD > bar_top(xx - PAD) - 6)
        f = band.astype(np.float32)[..., None]; rgb = rgb * (1 - f) + Prgb * f; A = np.maximum(A, band.astype(np.float32))
    frames.append(np.dstack([rgb, A * 255]).clip(0, 255).astype(np.uint8)); print(k, 'dy', dy, 'grip', grip_x)
U = np.zeros(shape, bool)
for f in frames: U |= f[..., 3] > 20
ys, xs = np.nonzero(U); bb = (xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5)
od = f'{D}/spr/sidepullS'; os.makedirs(od, exist_ok=True)
for f in os.listdir(od): os.remove(f'{od}/{f}')
for i, f in enumerate(frames): Image.fromarray(f, 'RGBA').crop(bb).save(f'{od}/f{i}.png')
json.dump(dict(canvas=[int(bb[2]-bb[0]), int(bb[3]-bb[1])], n=len(frames), src=use), open(f'{od}/info.json', 'w'))
