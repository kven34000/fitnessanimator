import numpy as np, sys, json
from PIL import Image
from scipy import ndimage as ndi
src=sys.argv[1]; prefix=sys.argv[2]; rows,cols=int(sys.argv[3]),int(sys.argv[4])
im=np.array(Image.open(src).convert('RGB')).astype(np.float32)
r,g,b=im[...,0],im[...,1],im[...,2]
mx=np.maximum(r,b)
spill=g-mx                       # green dominance
a=1-np.clip((spill-25)/(90-25),0,1)   # 0 on pure green, 1 on character
# despill: limit green to max(r,b) near edges
g2=np.where(spill>0,mx+np.clip(spill,0,None)*0.0,g)
out=np.dstack([r,g2,b,a*255]).clip(0,255).astype(np.uint8)
# remove tiny specks
solid=a>0.5
lab,n=ndi.label(solid); sizes=ndi.sum(solid,lab,range(1,n+1))
H,W=a.shape
cells={}
cw=W/cols; rowh=H/rows
for i,s_ in enumerate(sizes):
  if s_<1500: continue
  ys,xs=np.nonzero(lab==i+1)
  key_=(int(ys.mean()//rowh),int(xs.mean()//cw))
  cells.setdefault(key_,[]).append(i+1)
sprites=[]
for key_ in sorted(cells):
  ls=cells[key_]
  if sum(sizes[l-1] for l in ls)<20000: continue
  m=np.isin(lab,ls); ys,xs=np.nonzero(m)
  sprites.append((ys.min(),ys.max(),xs.min(),xs.max(),ls))
BOX=[]
for k,(y0,y1,x0,x1,l) in enumerate(sprites):
  m=ndi.binary_dilation(np.isin(lab,l),iterations=6)
  o=out.copy(); o[...,3]=(o[...,3]*m).astype(np.uint8)
  pad=8; crop=Image.fromarray(o).crop((max(0,x0-pad),max(0,y0-pad),min(W,x1+pad),min(H,y1+pad)))
  crop.save(f'{prefix}{k}.png'); print(k,crop.size); BOX.append([int(max(0,x0-pad)),int(max(0,y0-pad)),int(min(W,x1+pad)),int(min(H,y1+pad))])
json.dump(BOX,open(prefix+'boxes.json','w'))
