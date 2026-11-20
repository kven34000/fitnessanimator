# reflect the legs (left of the shorts) across their own axis so prone-drawn legs become face-up
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, dst, rows, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
A = np.asarray(Image.open(src).convert('RGB')).copy()
H, W = A.shape[:2]; ch, cw = H // rows, W // cols
key = lambda a: 1 - np.clip((a[..., 1].astype(float) - np.maximum(a[..., 0], a[..., 2]) - 25) / 65, 0, 1)
for r in range(rows):
    for c in range(cols):
        C = A[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
        m = key(C) > 0.5
        lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n+1)); m = lab == (np.argmax(sz) + 1)
        dark = (C.max(2) < 70) & m
        dl, dn = ndi.label(ndi.binary_opening(dark, iterations=2))
        if dn == 0: continue
        comps = []
        for i in range(1, dn+1):
            ys, xs = np.nonzero(dl == i)
            if len(xs) > 1500: comps.append((xs.mean(), xs.min(), xs.max(), len(xs)))
        # shorts = biggest dark blob not at far right (hair) and not at far left (shoes)
        comps.sort(key=lambda t: -t[3])
        xs_all = np.nonzero(m)[1]; L, R = xs_all.min(), xs_all.max()
        shorts = [t for t in comps if L + 0.25*(R-L) < t[0] < L + 0.75*(R-L)]
        if not shorts: print('no shorts', r, c); continue
        xcut = int(shorts[0][1]) + 6
        X = np.arange(L, xcut); cen = []
        for x in X:
            ys = np.nonzero(m[:, x])[0]; cen.append((ys.min() + ys.max()) / 2)
        cen = np.array(cen)
        # fit axis on thigh/shin part only (exclude shoes: first 18%)
        k0 = int(len(X) * 0.18); p0 = np.polyfit(X[k0:], cen[k0:], 1)
        # pivot at the hip, choose the line so that the flipped heel lands on the original floor level
        yfloor = max(np.nonzero(m[:, x])[0].max() for x in range(L, L + 60))
        xh = L + 12; ytop = np.nonzero(m[:, xh])[0].min()
        hy = np.polyval(p0, xcut); ay = (yfloor + ytop) / 2
        p = np.array([(hy - ay) / (xcut - xh), hy - (hy - ay) / (xcut - xh) * xcut])
        out = C.copy(); out[:, L:xcut] = [0, 255, 0]
        for x in range(L, xcut):
            cy = np.polyval(p, x)
            ys = np.arange(ch); sy = np.round(2*cy - ys).astype(int)
            ok = (sy >= 0) & (sy < ch)
            col = np.zeros((ch, 3), np.uint8); col[:] = [0, 255, 0]
            col[ok] = C[sy[ok], x]
            out[:, x] = col
        A[r*ch:(r+1)*ch, c*cw:(c+1)*cw] = out
        print(r, c, 'cut', xcut, 'axis', p)
Image.fromarray(A).save(dst)
