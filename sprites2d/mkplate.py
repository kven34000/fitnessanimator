# synthetic plate: original sheet with the person (from _noeq) painted green
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
n = sys.argv[1]; S='/home/claude/p2d/sheets'
O = np.asarray(Image.open(f'{S}/{n}.png').convert('RGB')).astype(np.float32)
N = np.asarray(Image.open(f'{S}/{n}_noeq.png').convert('RGB').resize((O.shape[1], O.shape[0]))).astype(np.float32)
key = lambda a: 1 - np.clip((a[...,1] - np.maximum(a[...,0], a[...,2]) - 25) / 65, 0, 1)
per = ndi.binary_dilation(key(N) > 0.3, iterations=6)
P = O.copy(); P[per] = [0, 255, 0]
Image.fromarray(P.astype(np.uint8)).save(f'{S}/{n}_plate.png')
