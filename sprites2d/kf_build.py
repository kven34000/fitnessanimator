# build per-keyframe meshes + weights for side squat morph
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
sheet=np.array(Image.open('squat_sheet.png').convert('RGB')).astype(int)
H,W,_=sheet.shape
K=[ # head neck sh el wr tip hip knee ank toe
 dict(head=(370,150),neck=(350,270),sh=(310,370),el=(310,600),wr=(360,760),tip=(395,890),hip=(330,760),knee=(360,1040),ank=(330,1380),toe=(470,1440)),
 dict(head=(1050,280),neck=(990,400),sh=(950,480),el=(1170,570),wr=(1300,450),tip=(1370,360),hip=(840,840),knee=(1070,1080),ank=(960,1390),toe=(1100,1440)),
 dict(head=(1720,380),neck=(1660,500),sh=(1610,560),el=(1830,580),wr=(2000,580),tip=(2120,575),hip=(1520,920),knee=(1790,1060),ank=(1660,1390),toe=(1820,1440)),
 dict(head=(2330,580),neck=(2290,710),sh=(2240,760),el=(2440,790),wr=(2620,790),tip=(2740,790),hip=(2150,1130),knee=(2430,1100),ank=(2290,1390),toe=(2430,1450)),
]
BONES=[('ank','knee'),('knee','hip'),('hip','neck'),('neck','head'),('neck','sh'),('sh','el'),('el','wr'),('wr','tip'),('ank','toe')]
PANEL=[(0,688),(688,1376),(1376,2064),(2064,2752)]
# panel 3 hand extends to edge; give it full width
PANEL[3]=(2040,2752); PANEL[2]=(1376,2080)
d=np.abs(sheet-sheet[5,5]).sum(2); cand=d<30
lab,_=ndi.label(cand); border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
fg=~np.isin(lab,list(border)); fg=ndi.binary_opening(fg,iterations=1)
def segdist(px,py,a,b):
  a=np.array(a,float);b=np.array(b,float);ab=b-a;L2=(ab**2).sum()
  t=np.clip(((px-a[0])*ab[0]+(py-a[1])*ab[1])/L2,0,1)
  return np.hypot(px-(a[0]+t*ab[0]),py-(a[1]+t*ab[1]))
out={'W':W,'H':H,'bones':BONES,'keys':[]}
STEP=10
ARMPOLY={0:[(240,320),(345,315),(375,400),(350,470),(345,560),(370,650),(390,710),(395,760),(430,840),(425,905),(380,910),(340,850),(318,770),(300,690),(275,600),(258,520),(235,430)]}
def build(k,J,m,suf,allowed):
  ys,xs=np.nonzero(m)
  gx=np.arange(xs.min()-STEP,xs.max()+2*STEP,STEP); gy=np.arange(ys.min()-STEP,ys.max()+2*STEP,STEP)
  mdd=ndi.binary_dilation(m,iterations=STEP)
  idx=-np.ones((len(gy),len(gx)),int); V=[]
  for j,y in enumerate(gy):
    for i,x in enumerate(gx):
      if 0<=x<W and 0<=y<H and mdd[y,x]: idx[j,i]=len(V); V.append((x,y))
  T=[]
  for j in range(len(gy)-1):
    for i in range(len(gx)-1):
      a,b,c,d_=idx[j,i],idx[j,i+1],idx[j+1,i],idx[j+1,i+1]
      if min(a,b,c,d_)>=0: T+=[int(a),int(b),int(d_),int(a),int(d_),int(c)]
  V=np.array(V,float)
  D=np.stack([segdist(V[:,0],V[:,1],J[a],J[b]) for a,b in BONES])
  if allowed is not None:
    for bi_,(a,b) in enumerate(BONES):
      if b not in allowed: D[bi_]+=1e4
  Wt=np.exp(-((D-D.min(0))/30.0)**2); order=np.argsort(-Wt,0)[:3]
  wt=np.take_along_axis(Wt,order,0); wt/=wt.sum(0)
  out['keys'].append({'k':k,'name':f'k{k}{suf}','J':J,'tex':f'key{k}{suf}.png','verts':V.tolist(),'tris':T,'bi':order.T.tolist(),'bw':wt.T.round(4).tolist()})
  print(k,suf,len(V))
for k,(J,(x0,x1)) in enumerate(zip(K,PANEL)):
  m=np.zeros_like(fg); m[:,x0:x1]=fg[:,x0:x1]
  lab2,n=ndi.label(m); sizes=ndi.sum(m,lab2,range(1,n+1)); keep=np.argmax(sizes)+1
  m=lab2==keep
  layers=[]
  if k in ARMPOLY:
    import cv2
    am=np.zeros((H,W),np.uint8); cv2.fillPoly(am,[np.array(ARMPOLY[k],np.int32)],1); am=(am>0)&m
    body=ndi.binary_fill_holes(ndi.binary_closing(m&~am,iterations=25))&ndi.binary_dilation(m,iterations=2)
    hole=(body&am).astype(np.uint8)*255
    img=cv2.inpaint(sheet.astype(np.uint8)[...,::-1].copy(),hole,9,cv2.INPAINT_TELEA)[...,::-1]
    layers=[('b',body,img,['ank','knee','hip','neck','head','toe']),('a',am,sheet.astype(np.uint8),['sh','el','wr','tip'])]
  else:
    layers=[('b',m,sheet.astype(np.uint8),None)]
  for (suf,lm,img,allowed) in layers:
    rgba=np.dstack([img,(ndi.gaussian_filter(lm.astype(float),0.8)*255).astype(np.uint8)])
    Image.fromarray(rgba,'RGBA').save(f'key{k}{suf}.png')
    build(k,J,lm,suf,allowed)
  continue
  ys,xs=np.nonzero(m)
  gx=np.arange(xs.min()-STEP,xs.max()+2*STEP,STEP); gy=np.arange(ys.min()-STEP,ys.max()+2*STEP,STEP)
  mdd=ndi.binary_dilation(m,iterations=STEP)
  idx=-np.ones((len(gy),len(gx)),int); V=[]
  for j,y in enumerate(gy):
    for i,x in enumerate(gx):
      if 0<=x<W and 0<=y<H and mdd[y,x]: idx[j,i]=len(V); V.append((x,y))
  T=[]
  for j in range(len(gy)-1):
    for i in range(len(gx)-1):
      a,b,c,d_=idx[j,i],idx[j,i+1],idx[j+1,i],idx[j+1,i+1]
      if min(a,b,c,d_)>=0: T+=[int(a),int(b),int(d_),int(a),int(d_),int(c)]
  V=np.array(V,float)
  D=np.stack([segdist(V[:,0],V[:,1],J[a],J[b]) for a,b in BONES])
  Wt=np.exp(-((D-D.min(0))/30.0)**2); order=np.argsort(-Wt,0)[:3]
  wt=np.take_along_axis(Wt,order,0); wt/=wt.sum(0)
  out['keys'].append({'J':J,'tex':f'key{k}.png','verts':V.tolist(),'tris':T,'bi':order.T.tolist(),'bw':wt.T.round(4).tolist()})
  print(k,len(V),len(T)//3)
json.dump(out,open('keys.json','w'))
