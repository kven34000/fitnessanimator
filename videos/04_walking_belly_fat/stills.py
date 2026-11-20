# python3 stills.py out_prefix t1 t2 ... -> tiles of 3x3 (640x360 each) with time labels
import sys, os
sys.argv_ = sys.argv[:]; sys.argv = ['x']
import render_walk as RW
R = RW.R
from PIL import Image, ImageDraw
from multiprocessing import Pool
def one(t):
    return Image.frombytes('RGB', (R.WD, R.HT), R.render(int(t * R.FPS))).resize((640, 360), Image.LANCZOS)
if __name__ == '__main__':
    pre = sys.argv_[1]; ts = [float(x) for x in sys.argv_[2:]]
    with Pool(2, initializer=R.init) as p: ims = p.map(one, ts)
    for k in range(0, len(ims), 9):
        o = Image.new('RGB', (1920, 1080)); d = ImageDraw.Draw(o)
        for i, (im, t) in enumerate(zip(ims[k:k + 9], ts[k:k + 9])):
            x, y = (i % 3) * 640, (i // 3) * 360; o.paste(im, (x, y)); d.rectangle([x, y, x + 70, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 4), f'{t:.1f}', fill=(255, 255, 0))
        o.save(f'{pre}_{k // 9}.png'); print(f'{pre}_{k // 9}.png')
