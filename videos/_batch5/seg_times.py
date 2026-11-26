# VDIR=<dir> python3 seg_times.py [frac]  -> one time per phrase (on the voice timeline)
import os, json, sys
VD = os.environ['VDIR']; f = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
sg = json.load(open(f'{VD}/vo/segs.json'))
print(' '.join(f'{a + f * (b - a):.2f}' for a, b in sg))
