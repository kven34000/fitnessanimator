"""Static equipment from a clean 'equipment only' plate.
inputs : sheets/<n>.png (orig), sheets/<n>_noeq.png (person only), sheets/<n>_plate.png (equipment only)
         optional sheets/<n>_mus.png
output : spr/<n>S/f{i}.png (+ _m), info.json — one fixed canvas, equipment = plate cell P (identical every frame),
         person from _noeq of each frame, shifted so that frame's own equipment (orig minus noeq) lies on the plate,
         equipment re-drawn on top wherever it covered the person in the original frame.
usage: python3 build_plate.py name rows cols plate_cell frames...
"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve
name, rows, cols, P = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
use = [int(x) for x in sys.argv[5:]]
D = '/home/claude/p2d'
def load(p, size=None):
    im = Image.open(p).convert('RGB')
    if size and im.size != size: im = im.resize(size, Image.LANCZOS)
    return np.array(im).astype(np.float32)
O = load(f'{D}/sheets/{name}.png'); H, W = O.shape[:2]
N = load(f'{D}/sheets/{name}_noeq.png', (W, H)); PL = load(f'{D}/sheets/{name}_plate.png', (W, H))
M = load(f'{D}/sheets/{name}_mus.png', (W, H)) if os.path.exists(f'{D}/sheets/{name}_mus.png') else None
def key(a): return 1 - np.clip((a[..., 1] - np.maximum(a[..., 0], a[..., 2]) - 25) / 65, 0, 1)
def despill(a):
    a = a.copy(); mx = np.maximum(a[..., 0], a[..., 2]); a[..., 1] = np.minimum(a[..., 1], mx + 8); return a
def clean(m, mn=800):
    lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > mn])
ao, an, ap = key(O), key(N), key(PL)
ch, cw = H / rows, W / cols
cells = [(int(i * ch), int(j * cw)) for i in range(rows) for j in range(cols)]
CH, CW = int(ch), int(cw)
def cell(a, k): y, x = cells[k]; return a[y:y + CH, x:x + CW]
MB = int(os.environ.get('PMB', 0))
def cellp(a, k):
    y, x = cells[k]; sub = a[y:y + CH + MB, x:x + CW]
    if sub.shape[0] < CH + MB:
        pad = np.zeros((CH + MB - sub.shape[0],) + sub.shape[1:], sub.dtype); sub = np.concatenate([sub, pad])
    return sub
def own(m):
    lab, n = ndi.label(m); keep = np.zeros_like(m)
    for i in range(1, n + 1):
        c = lab == i
        if c[:CH].sum() > 0.5 * c.sum(): keep |= c
    return keep
# plate (cell P)
pa = cell(ap, P) * clean(cell(ap, P) > 0.5, 2000); prgb = cell(despill(PL), P)
plate_mask = pa > 0.5
PAD = 160
out_shape = (CH + 2 * PAD, CW + 2 * PAD)
def put(sub, dy, dx):
    o = np.zeros(out_shape + sub.shape[2:], sub.dtype)
    o[PAD + dy:PAD + dy + sub.shape[0], PAD + dx:PAD + dx + sub.shape[1]] = sub; return o
Pa = put(pa, 0, 0); Prgb = put(prgb, 0, 0)
frames = []
for k in use:
    # this frame's own equipment = orig opaque & not person
    e = (cell(ao, k) > 0.5) & (cell(an, k) < 0.3); e = clean(ndi.binary_opening(e, iterations=2), 500)
    cor = fftconvolve(plate_mask.astype(np.float32), e[::-1, ::-1].astype(np.float32), mode='same')
    cy, cx = np.array(cor.shape) // 2; R = 150
    win = cor[cy - R:cy + R, cx - R:cx + R]; iy, ix = np.unravel_index(np.argmax(win), win.shape)
    dy, dx = iy - R, ix - R
    na = cellp(an, k) if MB else cell(an, k); na = na * ndi.binary_dilation(own(clean(na > 0.5, 1500)), iterations=4)
    Na = put(na, dy, dx); Nrgb = put((cellp if MB else cell)(despill(N), k), dy, dx)
    Ea = put(e.astype(np.float32), dy, dx)  # where the equipment was visible in the original frame
    # equipment in front of the person where the original frame showed equipment over the person's silhouette
    front = (Ea > 0.5) & (Pa > 0.5) & (ndi.binary_dilation(Na > 0.5, iterations=3))
    a_eq = Pa.copy()
    A = np.clip(Na + a_eq * (1 - Na), 0, 1)
    rgb = (Nrgb * Na[..., None] + Prgb * (a_eq * (1 - Na))[..., None]) / np.maximum(A, 1e-4)[..., None]
    f = front.astype(np.float32)[..., None]
    rgb = rgb * (1 - f) + Prgb * f; A = np.maximum(A, front.astype(np.float32))
    img = np.dstack([rgb, A * 255]).clip(0, 255).astype(np.uint8)
    mk = None
    if M is not None:
        C = put((cellp if MB else cell)(M, k), dy, dx); r, g, b = C[..., 0], C[..., 1], C[..., 2]
        chans = []
        for m in ((b > 170) & (r < 110) & (g < 110), (r > 190) & (g > 190) & (b < 110), (r > 170) & (b > 170) & (g < 110), (g > 170) & (b > 170) & (r < 110)):
            m = ndi.binary_closing(ndi.binary_opening(m, iterations=1), iterations=2) & (Na > 0.5) & ~front
            chans.append((ndi.gaussian_filter(m.astype(np.float32), 1.0) * 255).clip(0, 255).astype(np.uint8))
        mk = np.dstack(chans)
    frames.append((img, mk)); print(name, k, 'shift', dy, dx)
U = np.zeros(out_shape, bool)
for img, _ in frames: U |= img[..., 3] > 20
ys, xs = np.nonzero(U); bb = (xs.min() - 4, ys.min() - 4, xs.max() + 5, ys.max() + 5)
od = f'{D}/spr/{name}S'; os.makedirs(od, exist_ok=True)
for f in os.listdir(od): os.remove(f'{od}/{f}')
for i, (img, mk) in enumerate(frames):
    Image.fromarray(img, 'RGBA').crop(bb).save(f'{od}/f{i}.png')
    if mk is not None: Image.fromarray(mk, 'RGBA').crop(bb).save(f'{od}/f{i}_m.png')
json.dump(dict(canvas=[int(bb[2] - bb[0]), int(bb[3] - bb[1])], n=len(frames), src=use), open(f'{od}/info.json', 'w'))
print('canvas', bb[2] - bb[0], bb[3] - bb[1])
