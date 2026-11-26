# VDIR=<dir> python3 lint_img.py  -> props (img) that would stick out of the 1920x1080 frame
import os, sys
sys.argv = ['x']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_b5 as RB
from PIL import Image
for e in RB.R.EL:
    if e['k'] != 'img' or e.get('h', 0) < 5: continue
    im = Image.open(e['path']); w = e['h'] * im.width / im.height
    x0, x1, y0, y1 = e['x'] - w / 2, e['x'] + w / 2, e['y'] - e['h'] / 2, e['y'] + e['h'] / 2
    if x0 < 10 or x1 > 1910 or y0 < 10 or y1 > 1070:
        print(f"{e['t0']:.1f}s {os.path.basename(os.path.dirname(e['path']))}/{os.path.basename(e['path'])} box x{x0:.0f}-{x1:.0f} y{y0:.0f}-{y1:.0f}")
