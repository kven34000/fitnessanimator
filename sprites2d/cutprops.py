# cut a 4x2 object sheet (cells may have drawn borders): inset each cell, key green, keep the biggest blob
import numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
src, prefix = sys.argv[1], sys.argv[2]; rows, cols = 2, 4; INS = int(sys.argv[3]) if len(sys.argv) > 3 else 16
im = np.array(Image.open(src).convert('RGB')).astype(np.float32); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
a = 1 - np.clip((g - np.maximum(r, b) - 25) / 65, 0, 1)
out = np.dstack([r, np.where(g > np.maximum(r, b), np.maximum(r, b), g), b, a * 255]).clip(0, 255).astype(np.uint8)
for i in range(rows):
    for j in range(cols):
        y0, y1, x0, x1 = int(i * H / rows) + INS, int((i + 1) * H / rows) - INS, int(j * W / cols) + INS, int((j + 1) * W / cols) - INS
        sub = out[y0:y1, x0:x1].copy(); m = sub[..., 3] > 128
        lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
        big = max(sz); keep = np.isin(lab, [q + 1 for q, s in enumerate(sz) if s > 0.08 * big])
        keep = ndi.binary_fill_holes(ndi.binary_dilation(keep, iterations=4)); sub[..., 3] = (sub[..., 3] * keep).astype(np.uint8)
        ys, xs = np.nonzero(sub[..., 3] > 128)
        Image.fromarray(sub).crop((xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7)).save(f'{prefix}{i * cols + j}.png')
