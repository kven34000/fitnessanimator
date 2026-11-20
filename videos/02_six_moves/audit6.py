import sys; sys.path.insert(0, '/home/claude/v2_6ex')
import render_6ex as X
R = X.R
from PIL import Image
import numpy as np
R.init()
res = {}; edge = {}
T = 0.0
while T < X.DUR:
    R.AUDIT = {'txt': [], 'chr': []}
    R.render(int(T * R.FPS))
    mask = Image.new('L', (R.WD, R.HT), 0)
    for al, (x, y) in R.AUDIT['chr']:
        mask.paste(255, (x, y), al.point(lambda v: 255 if v > 200 else 0))
    if R.CAM: mask = R.apply_cam(mask, T)
    m = np.array(mask) > 0
    for key, (x0, y0, x1, y1) in R.AUDIT['txt']:
        if x0 < -5 or x1 > R.WD + 5 or y0 < -5: edge.setdefault((key[0], key[1], key[2]), []).append(T)
        x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(R.WD, int(x1)), min(R.HT, int(y1))
        if x1 <= x0 or y1 <= y0: continue
        ov = m[y0:y1, x0:x1].sum()
        if ov > 300: res.setdefault((key[0], key[1], key[2]), []).append((T, int(ov)))
    T += 0.5
print('SUBT', [t for t,o in res.get(('SUB','sub',''),[])])
for k, v in sorted(res.items(), key=lambda a: a[1][0][0]):
    print('OVERLAP', k, v[0][0], '-', v[-1][0], 'max', max(o for _, o in v))
for k, v in sorted(edge.items(), key=lambda a: a[1][0]):
    print('EDGE', k, v[0], '-', v[-1])
