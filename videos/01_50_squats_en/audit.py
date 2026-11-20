import sys; sys.path.insert(0, '/home/claude/work'); sys.path.insert(0, '/home/claude/en')
import render_en as RE
R = RE.R
from timewarp import to_ru, EN_DUR
from PIL import Image
import numpy as np
R.init()
res = {}
for i in range(int(EN_DUR * 4)):
    T = i / 4
    R.AUDIT = {'txt': [], 'chr': []}
    R.render(to_ru(T) * R.FPS)
    mask = Image.new('L', (R.WD, R.HT), 0)
    for al, (x, y) in R.AUDIT['chr']:
        # character core only (skip faint glow halo)
        mask.paste(255, (x, y), al.point(lambda v: 255 if v > 200 else 0))
    m = np.array(mask) > 0
    for key, (x0, y0, x1, y1) in R.AUDIT['txt']:
        x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(R.WD, int(x1)), min(R.HT, int(y1))
        if x1 <= x0 or y1 <= y0: continue
        ov = m[y0:y1, x0:x1].sum()
        if ov > 300:
            k2 = (key[0], key[1], key[2])
            res.setdefault(k2, []).append((T, int(ov)))
for k, v in sorted(res.items(), key=lambda a: a[1][0][0]):
    print(k, 'EN t', v[0][0], '-', v[-1][0], 'max px', max(o for _, o in v))
