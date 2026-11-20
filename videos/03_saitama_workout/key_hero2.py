import numpy as np, json
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
im=np.asarray(Image.open('/home/claude/v3_sai/hero2/sheet_src.png').convert('RGB')).astype(np.float32)
H,W,_=im.shape; R,G,B=im[...,0],im[...,1],im[...,2]
spill=G-np.maximum(R,B)
a=np.clip(1-(spill-40)/80,0,1)          # >120 fully transparent, <40 opaque
# despill: clamp green to max(R,B) where greenish
G2=np.where(spill>0, np.maximum(R,B)+np.clip(spill,0,0)*0, G)
rgb=np.stack([R,np.minimum(G,np.maximum(R,B)+8),B],-1)
rows,cols=2,4; cw,ch=W/cols,H/rows; info=[]
for r in range(rows):
  for c in range(cols):
    x0,y0,x1,y1=int(c*cw),int(r*ch),int((c+1)*cw),int((r+1)*ch)
    al=a[y0:y1,x0:x1]; m=al>0.5
    lab,n=ndi.label(m); sz=ndi.sum(m,lab,range(1,n+1)); keep=np.isin(lab,1+np.nonzero(sz>2000)[0])
    keep=ndi.binary_fill_holes(ndi.binary_dilation(keep,iterations=2)) & (al>0.02)
    alc=al*keep
    ys,xs=np.nonzero(alc>0.5); bx0,bx1,by0,by1=xs.min(),xs.max(),ys.min(),ys.max()
    sub=rgb[y0:y1,x0:x1]
    # body centre: yellow suit pixels
    yel=(sub[...,0]>180)&(sub[...,1]>150)&(sub[...,2]<120)&keep
    yx=np.nonzero(yel)[1]; bodyx=float(np.median(yx))
    py0,px0=max(by0-4,0),max(bx0-4,0)
    out=np.dstack([sub,alc*255]).clip(0,255).astype(np.uint8)[py0:by1+5,px0:bx1+5]
    i=r*cols+c; Image.fromarray(out,'RGBA').save(f'hero2/p{i}.png')
    info.append(dict(i=i,w=out.shape[1],h=out.shape[0],ax=bodyx-px0,ay=by1-py0,top=by0))
json.dump(info,default=float,fp=open('hero2/info.json','w'),indent=1)
for d in info: print(d)
