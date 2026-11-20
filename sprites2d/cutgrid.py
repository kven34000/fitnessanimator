import numpy as np, sys, json
from PIL import Image
from scipy import ndimage as ndi
src, prefix, rows, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
im = np.array(Image.open(src).convert('RGB')).astype(np.float32)
H, W = im.shape[:2]; ch, cw = H / rows, W / cols
r, g, b = im[..., 0], im[..., 1], im[..., 2]
a = 1 - np.clip((g - np.maximum(r, b) - 25) / 65, 0, 1)
out = np.dstack([r, np.where(g > np.maximum(r, b), np.maximum(r, b), g), b, a * 255]).clip(0, 255).astype(np.uint8)
BOX = []; k = 0
for i in range(rows):
    for j in range(cols):
        y0, y1, x0, x1 = int(i * ch), int((i + 1) * ch), int(j * cw), int((j + 1) * cw)
        sub = out[y0:y1, x0:x1].copy(); m = sub[..., 3] > 128
        lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
        keep = np.isin(lab, [q + 1 for q, s in enumerate(sz) if s > 1500])
        keep = ndi.binary_dilation(keep, iterations=6); sub[..., 3] = (sub[..., 3] * keep).astype(np.uint8)
        ys, xs = np.nonzero(sub[..., 3] > 128)
        bx = [int(max(0, xs.min() - 8)), int(max(0, ys.min() - 8)), int(min(x1 - x0, xs.max() + 8)), int(min(y1 - y0, ys.max() + 8))]
        Image.fromarray(sub).crop(bx).save(f'{prefix}{k}.png')
        BOX.append([bx[0] + x0, bx[1] + y0, bx[2] + x0, bx[3] + y0]); k += 1
json.dump(BOX, open(prefix + 'boxes.json', 'w')); print(k)
