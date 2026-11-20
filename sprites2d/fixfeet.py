import numpy as np, sys, json
from PIL import Image
P = sys.argv[1]; donor = int(sys.argv[2]); targets = [int(x) for x in sys.argv[3:]]
def runs(row):
    m = row > 128; r = []; i = 0; n = len(m)
    while i < n:
        if m[i]:
            j = i
            while j < n and m[j]: j += 1
            r.append((i, j)); i = j
        else: i += 1
    r = sorted(r, key=lambda a: a[1] - a[0], reverse=True)[:2]
    return sorted(r)
D = np.array(Image.open(f'spr/{P}/f{donor}.png').convert('RGBA'))
Dm = np.array(Image.open(f'spr/{P}/f{donor}_m.png').convert('RGBA')) if __import__('os').path.exists(f'spr/{P}/f{donor}_m.png') else None
dy = np.where(D[..., 3].max(1) > 128)[0][-1]
for k in targets:
    T = np.array(Image.open(f'spr/{P}/f{k}.png').convert('RGBA'))
    ty = np.where(T[..., 3].max(1) > 128)[0][-1]
    yt = ty - 40  # seam row in target (above the cut shoe tops)
    rt = runs(T[yt, :, 3])
    wt = [b - a for a, b in rt]
    # find donor row with best matching leg widths, searching above the donor's shoes
    best = None
    for y in range(dy - 300, dy - 20):
        rd = runs(D[y, :, 3])
        if len(rd) < 2: continue
        err = sum(abs((b - a) - w) for (a, b), w in zip(rd, wt))
        if best is None or err < best[0]: best = (err, y, rd)
    err, yd, rd = best
    add = dy - yd + 10
    H = yt + add + 1
    out = np.zeros((max(H, T.shape[0]), T.shape[1], 4), np.uint8); out[:T.shape[0]] = T
    out[yt:] = 0; out[:yt] = T[:yt]
    mo = None
    if __import__('os').path.exists(f'spr/{P}/f{k}_m.png'):
        M = np.array(Image.open(f'spr/{P}/f{k}_m.png').convert('RGBA'))
        mo = np.zeros_like(out); mo[:yt] = M[:yt]
    for (ta, tb), (da, db) in zip(rt, rd):
        cxT = (ta + tb) / 2; cxD = (da + db) / 2
        half = int(max(tb - ta, db - da) * 1.6)
        x0d = int(cxD - half); x1d = int(cxD + half)
        seg = D[yd:dy + 10, max(0, x0d):min(D.shape[1], x1d)]
        xo = int(cxT - (cxD - max(0, x0d)))
        for yy in range(seg.shape[0]):
            Y = yt + yy
            if Y >= out.shape[0]: break
            for_x0 = max(0, xo); sx0 = for_x0 - xo
            w = min(seg.shape[1] - sx0, out.shape[1] - for_x0)
            src = seg[yy, sx0:sx0 + w]
            dst = out[Y, for_x0:for_x0 + w]
            a = src[:, 3:4].astype(float) / 255
            dst[:] = (src * a + dst * (1 - a)).astype(np.uint8)
            dst[:, 3] = np.maximum(dst[:, 3], src[:, 3])
    Image.fromarray(out).save(f'spr/{P}/f{k}.png')
    if mo is not None: Image.fromarray(mo).save(f'spr/{P}/f{k}_m.png')
    print(k, 'seam', yt, 'donor row', yd, 'err', err, 'new h', out.shape[0], 'old h', T.shape[0])
