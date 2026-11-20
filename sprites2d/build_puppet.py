import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
im=np.array(Image.open('/home/claude/w3d/hero_apose.png').convert('RGB')).astype(int)
H,W,_=im.shape
bg=np.array([198,198,200])
d=np.abs(im-im[5,5]).sum(2)
cand=d<30
lab,n=ndi.label(cand)
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
bgm=np.isin(lab,list(border))
fg=~bgm
fg=ndi.binary_opening(fg,iterations=1)
J={'pelvis':(850,1250),'spine2':(850,860),'neck':(850,540),'headtop':(850,40),
'R_sh':(540,660),'R_el':(440,920),'R_wr':(365,1190),'R_tip':(360,1460),
'L_sh':(1160,660),'L_el':(1260,920),'L_wr':(1345,1190),'L_tip':(1350,1460),
'R_hip':(730,1300),'R_knee':(690,1770),'R_ank':(640,2250),'R_toe':(510,2430),
'L_hip':(970,1300),'L_knee':(1010,1770),'L_ank':(1070,2250),'L_toe':(1190,2430)}
# bone: name -> (j0,j1,layer,parent)
BONES={'spineLow':('pelvis','spine2','body',None),'spineUp':('spine2','neck','body','spineLow'),'head':('neck','headtop','body','spineUp'),
}
for S in 'RL':
  BONES.update({f'{S}_clav':('spine2',f'{S}_sh','body','spineUp'),f'{S}_up':(f'{S}_sh',f'{S}_el','arm'+S,f'{S}_clav'),
   f'{S}_fore':(f'{S}_el',f'{S}_wr','arm'+S,f'{S}_up'),f'{S}_hand':(f'{S}_wr',f'{S}_tip','arm'+S,f'{S}_fore'),
   f'{S}_pel':('pelvis',f'{S}_hip','body','spineLow'),f'{S}_thigh':(f'{S}_hip',f'{S}_knee','leg'+S,f'{S}_pel'),
   f'{S}_shin':(f'{S}_knee',f'{S}_ank','leg'+S,f'{S}_thigh'),f'{S}_foot':(f'{S}_ank',f'{S}_toe','leg'+S,f'{S}_shin')})
names=list(BONES)
yy,xx=np.mgrid[0:H,0:W]
def segdist(px,py,a,b):
  a=np.array(a,float);b=np.array(b,float);ab=b-a;L2=(ab**2).sum()
  t=np.clip(((px-a[0])*ab[0]+(py-a[1])*ab[1])/L2,0,1)
  return np.hypot(px-(a[0]+t*ab[0]),py-(a[1]+t*ab[1])),t
# pixel layer assignment by nearest bone (downsampled for speed)
ds=4
sx,sy=xx[::ds,::ds],yy[::ds,::ds]
D=np.stack([segdist(sx,sy,J[BONES[b][0]],J[BONES[b][1]])[0] for b in names])
# clavicle/pelvis bones get bigger reach (torso mass)
for i,b in enumerate(names):
  if BONES[b][2]=='body': D[i]*=0.85
  if b in('R_pel','L_pel'): D[i]*=1.6
near=D.argmin(0)
layer_of=np.array([BONES[b][2] for b in names])
L=layer_of[near]
fgs=fg[::ds,::ds]
# shorts pixels: dark/black or red trim in shorts box -> keep layer from nearest, but shorts over thighs go to legs with pelvis blend
layers=['legR','legL','body','armR','armL']
out={'W':W,'H':H,'joints':J,'bones':{b:list(BONES[b]) for b in names},'layers':[]}
STEP=12
for ly in layers:
  m=(L==ly)&fgs
  m=np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W,H),Image.NEAREST))>0
  m&=fg
  # overlap: dilate layer mask within fg so seams overlap
  md=ndi.binary_dilation(m,iterations=10 if ly=='body' else 6)&fg
  rgba=np.dstack([im.astype(np.uint8),(ndi.gaussian_filter(md.astype(float),1.0)*255).astype(np.uint8)])
  Image.fromarray(rgba,'RGBA').save(f'tex_{ly}.png')
  ys,xs=np.nonzero(md); x0,x1,y0,y1=xs.min()-STEP,xs.max()+STEP,ys.min()-STEP,ys.max()+STEP
  gx=np.arange(x0,x1+STEP,STEP); gy=np.arange(y0,y1+STEP,STEP)
  idx=-np.ones((len(gy),len(gx)),int); verts=[]; tris=[]
  mdd=ndi.binary_dilation(md,iterations=STEP)
  for j,y in enumerate(gy):
    for i,x in enumerate(gx):
      if 0<=x<W and 0<=y<H and mdd[y,x]: idx[j,i]=len(verts); verts.append((x,y))
  for j in range(len(gy)-1):
    for i in range(len(gx)-1):
      a,b,c,d_=idx[j,i],idx[j,i+1],idx[j+1,i],idx[j+1,i+1]
      if min(a,b,c,d_)>=0: tris+= [a,b,d_,a,d_,c]
  V=np.array(verts,float)
  # weights: bones of this layer + their parents
  cand=[b for b in names if BONES[b][2]==ly]
  cand+= [BONES[b][3] for b in cand if BONES[b][3] and BONES[b][3] not in cand]
  Dv=np.stack([segdist(V[:,0],V[:,1],J[BONES[b][0]],J[BONES[b][1]])[0] for b in cand])
  for k,b in enumerate(cand):
    if BONES[b][2]!=ly: Dv[k]*=1.8   # parent bones from other layer weaker
  sig=45.0
  Wt=np.exp(-((Dv-Dv.min(0))/sig)**2)
  # keep top4
  order=np.argsort(-Wt,0)[:4]
  wt=np.take_along_axis(Wt,order,0); wt/=wt.sum(0)
  bi=np.array([names.index(cand[k]) for k in range(len(cand))])[order]
  out['layers'].append({'name':ly,'tex':f'tex_{ly}.png','verts':V.tolist(),'tris':[int(v) for v in tris],'bi':bi.T.tolist(),'bw':wt.T.round(4).tolist()})
  print(ly,len(V),len(tris)//3,cand)
out['names']=names
json.dump(out,open('puppet.json','w'))
Image.fromarray((fg*255).astype(np.uint8)).save('fg.png')
