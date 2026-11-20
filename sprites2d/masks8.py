import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as ndi
def key(im):
  r,g,b=im[...,0],im[...,1],im[...,2]; spill=g-np.maximum(r,b)
  return 1-np.clip((spill-25)/65,0,1)
for name in sys.argv[1:]:
  orig=np.array(Image.open(f'sheets/{name}.png').convert('RGB')).astype(np.float32)
  mus=np.array(Image.open(f'sheets/{name}_mus.png').convert('RGB')).astype(np.float32)
  if mus.shape!=orig.shape: mus=np.array(Image.fromarray(mus.astype(np.uint8)).resize((orig.shape[1],orig.shape[0]),Image.LANCZOS)).astype(np.float32)
  boxes=json.load(open(f'spr/{name}/fboxes.json'))
  ao=key(orig); am=key(mus)
  for k,(x0,y0,x1,y1) in enumerate(boxes):
    A=ao[y0:y1,x0:x1]
    best=(1e18,0,0)
    for dy in range(-24,25,3):
      for dx in range(-24,25,3):
        B=am[max(0,y0+dy):y1+dy, max(0,x0+dx):x1+dx]
        if B.shape!=A.shape: continue
        e=((A-B)**2).mean()
        if e<best[0]: best=(e,dx,dy)
    _,dx,dy=best
    for ddy in range(dy-2,dy+3):
      for ddx in range(dx-2,dx+3):
        B=am[y0+ddy:y1+ddy, x0+ddx:x1+ddx]
        if B.shape!=A.shape: continue
        e=((A-B)**2).mean()
        if e<best[0]: best=(e,ddx,ddy)
    _,dx,dy=best
    C=mus[y0+dy:y1+dy, x0+dx:x1+dx]
    r,g,b=C[...,0],C[...,1],C[...,2]
    blue=(b>170)&(r<110)&(g<110)
    yel=(r>190)&(g>190)&(b<110)
    mag=(r>170)&(b>170)&(g<110)
    cya=(g>170)&(b>170)&(r<110)
    chans=[]
    for m in (blue,yel,mag,cya):
      m=ndi.binary_opening(m,iterations=1); m=ndi.binary_closing(m,iterations=2)
      chans.append((ndi.gaussian_filter(m.astype(np.float32),1.0)*255).clip(0,255).astype(np.uint8))
    out=np.dstack(chans)
    Image.fromarray(out,'RGBA').save(f'spr/{name}/f{k}_m.png')
    print(name,k,'shift',dx,dy,'err',round(best[0],4),'px',[int((c>128).sum()) for c in chans])
