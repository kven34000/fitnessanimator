"""Static-equipment rebuild.
orig sheet  : sheets/<name>.png           (character + equipment, 8 cells)
noeq sheet  : sheets/<name>_noeq.png      (same image with equipment removed by Magnific edit)
mus sheet   : sheets/<name>_mus.png       (optional muscle colour coding)
Output      : spr/<name>S/f{k}.png (+ f{k}_m.png) — all frames on one common canvas, equipment identical
              in every frame (median over registered frames), character registered to the equipment.
usage: python3 build_equip.py name rows cols [frames...]
"""
import sys, os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

name, rows, cols = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
D = '/home/claude/p2d'
def load(p, size=None):
    im = Image.open(p).convert('RGB')
    if size and im.size != size: im = im.resize(size, Image.LANCZOS)
    return np.array(im).astype(np.float32)
O = load(f'{D}/sheets/{name}.png'); H, W = O.shape[:2]
N = load(f'{D}/sheets/{name}_noeq.png', (W, H))
M = load(f'{D}/sheets/{name}_mus.png', (W, H)) if os.path.exists(f'{D}/sheets/{name}_mus.png') else None
def key(a):
    return 1 - np.clip((a[..., 1] - np.maximum(a[..., 0], a[..., 2]) - 25) / 65, 0, 1)
def despill(a):
    a = a.copy(); mx = np.maximum(a[..., 0], a[..., 2]); a[..., 1] = np.minimum(a[..., 1], mx + 8); return a
ao, an = key(O), key(N)
E = (ao > 0.5) & (an < 0.35)
E = ndi.binary_opening(E, iterations=2)
lab, n = ndi.label(E); sz = ndi.sum(E, lab, range(1, n + 1))
E = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > 800])
E = ndi.binary_dilation(E, iterations=2) & (ao > 0.3)
ch, cw = H / rows, W / cols
cells = [(int(i * ch), int((i + 1) * ch), int(j * cw), int((j + 1) * cw)) for i in range(rows) for j in range(cols)]
use = [int(x) for x in sys.argv[4:]] or list(range(len(cells)))
ref = None; shifts = []
CH = int(ch); CW = int(cw)
for k in use:
    y0, y1, x0, x1 = cells[k]
    e = E[y0:y0 + CH, x0:x0 + CW].astype(np.float32)
    if ref is None: ref = e; shifts.append((0, 0)); continue
    cor = fftconvolve(ref, e[::-1, ::-1], mode='same')
    cy, cx = np.array(cor.shape) // 2; R = 160
    win = cor[cy - R:cy + R, cx - R:cx + R]
    iy, ix = np.unravel_index(np.argmax(win), win.shape)
    shifts.append((iy - R, ix - R))
print(name, 'shifts', shifts)
PAD = 200
def shifted(arr, k, dy, dx):
    y0, y1, x0, x1 = cells[k]
    out = np.zeros((CH + 2 * PAD, CW + 2 * PAD) + arr.shape[2:], arr.dtype)
    sub = arr[y0:y0 + CH, x0:x0 + CW]
    out[PAD + dy:PAD + dy + sub.shape[0], PAD + dx:PAD + dx + sub.shape[1]] = sub
    return out
# static equipment = median vote over registered frames
eqs = []; eqc = []
for k, (dy, dx) in zip(use, shifts):
    eqs.append(shifted(E.astype(np.float32), k, dy, dx)); eqc.append(shifted(despill(O), k, dy, dx))
eqs = np.stack(eqs); vote = eqs.mean(0) > 0.45
colr = np.zeros(vote.shape + (3,), np.float32)
for i in range(len(eqs)):  # take colour from the first frame where the pixel is equipment
    m = (eqs[i] > 0.5) & (colr.sum(-1) == 0) & vote
    colr[m] = eqc[i][m]
eqA = vote.astype(np.float32)
os.makedirs(f'{D}/spr/{name}S', exist_ok=True)
boxes = []
for idx, (k, (dy, dx)) in enumerate(zip(use, shifts)):
    ca = shifted(an, k, dy, dx)
    # keep only the character components (drop specks)
    cm = ca > 0.5; lab, n = ndi.label(cm); sz = ndi.sum(cm, lab, range(1, n + 1))
    keep = ndi.binary_dilation(np.isin(lab, [i + 1 for i, s in enumerate(sz) if s > 1500]), iterations=4)
    ca = ca * keep
    cc = shifted(despill(N), k, dy, dx)
    a = np.clip(ca + eqA * (1 - ca), 0, 1)
    rgb = (cc * ca[..., None] + colr * (eqA * (1 - ca))[..., None]) / np.maximum(a, 1e-4)[..., None]
    Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA').save(f'{D}/spr/{name}S/f{idx}.png')
    if M is not None:
        C = shifted(M, k, dy, dx); r, g, b = C[..., 0], C[..., 1], C[..., 2]
        chans = []
        for m in ((b > 170) & (r < 110) & (g < 110), (r > 190) & (g > 190) & (b < 110), (r > 170) & (b > 170) & (g < 110), (g > 170) & (b > 170) & (r < 110)):
            m = ndi.binary_closing(ndi.binary_opening(m, iterations=1), iterations=2) & (ca > 0.5)
            chans.append((ndi.gaussian_filter(m.astype(np.float32), 1.0) * 255).clip(0, 255).astype(np.uint8))
        Image.fromarray(np.dstack(chans), 'RGBA').save(f'{D}/spr/{name}S/f{idx}_m.png')
    boxes.append([0, 0, CW + 2 * PAD, CH + 2 * PAD])
json.dump(dict(boxes=boxes, canvas=[CW + 2 * PAD, CH + 2 * PAD], foot=None), open(f'{D}/spr/{name}S/info.json', 'w'))
print('ok', len(use))
# crop all frames to the union bbox so they stay on one common canvas
fs = sorted([f for f in os.listdir(f'{D}/spr/{name}S') if f.endswith('.png')])
ims = {f: Image.open(f'{D}/spr/{name}S/{f}') for f in fs}
U = None
for f, im in ims.items():
    if f.endswith('_m.png'): continue
    a = np.array(im)[..., 3] > 20
    U = a if U is None else (U | a)
ys, xs = np.nonzero(U); bb = (int(xs.min()) - 4, int(ys.min()) - 4, int(xs.max()) + 5, int(ys.max()) + 5)
for f, im in ims.items(): im.crop(bb).save(f'{D}/spr/{name}S/{f}')
json.dump(dict(canvas=[bb[2] - bb[0], bb[3] - bb[1]], n=len(use)), open(f'{D}/spr/{name}S/info.json', 'w'))
print('canvas', bb[2] - bb[0], bb[3] - bb[1])
