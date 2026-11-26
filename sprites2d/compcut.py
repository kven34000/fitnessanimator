# cut a sheet whose figures are not on a clean grid: connected components (small dilation), biggest N, ordered by row then x
# python3 compcut.py sheet.png spr/<name>/f N [ROWS]
import numpy as np, sys, json
from PIL import Image
from scipy import ndimage as ndi
src, prefix, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); ROWS = int(sys.argv[4]) if len(sys.argv) > 4 else 2
im = np.array(Image.open(src).convert('RGB')).astype(np.float32); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
a = 1 - np.clip((g - np.maximum(r, b) - 25) / 65, 0, 1)
out = np.dstack([r, np.where(g > np.maximum(r, b), np.maximum(r, b), g), b, a * 255]).clip(0, 255).astype(np.uint8)
m = ndi.binary_dilation(a > 0.5, iterations=5)
lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
big = sorted(range(n), key=lambda i: -sz[i])[:N]
items = []
for i in big:
    ys, xs = np.nonzero(lab == i + 1)
    items.append((int(ys.mean() // (H / ROWS)), int(xs.min()), i, int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())))
items.sort(); BOX = []
for k, (_, _, i, y0, y1, x0, x1) in enumerate(items):
    sub = out[y0:y1 + 1, x0:x1 + 1].copy()
    sub[..., 3] = (sub[..., 3] * (lab[y0:y1 + 1, x0:x1 + 1] == i + 1)).astype(np.uint8)
    Image.fromarray(sub).save(f'{prefix}{k}.png'); BOX.append([x0, y0, x1, y1])
json.dump(BOX, open(prefix + 'boxes.json', 'w')); print(len(BOX))
