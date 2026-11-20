import numpy as np
from PIL import Image
from scipy import ndimage as ndi
im=np.array(Image.open('/home/claude/w3d/hero_apose.png').convert('RGB')).astype(int)
H,W,_=im.shape
lum=im[...,0]*0.3+im[...,1]*0.59+im[...,2]*0.11
dark=(lum<185)
dark=ndi.binary_closing(dark,iterations=3)
dark=ndi.binary_dilation(dark,iterations=1)
fg=np.array(Image.open('fg.png'))>0
free=fg&~dark
core=ndi.binary_erosion(free,iterations=7)
lab,n=ndi.label(core)
MUS=['pecs','abs','obliques','delts','biceps','triceps','forearms','lats','traps','quads','hams','glutes','calves','lowback','serratus','spare']
SEEDS={
 'abs':[(800,840,(700,780,1000,1000)),(900,840,(700,780,1000,1000)),(800,905,(700,780,1000,1000)),(900,905,(700,780,1000,1000)),(800,965,(700,780,1000,1000)),(900,965,(700,780,1000,1000))],
 'pecs':[(730,700,(590,600,846,778)),(970,700,(854,600,1110,778))],
 'delts':[(510,630,(400,560,600,820)),(1190,630,(1100,560,1300,820))],
 'biceps':[(480,820),(1225,820)],
 'quads':[(650,1450),(1050,1450),(735,1690),(955,1690)],
}
idm=np.zeros((H,W)); st=np.zeros((H,W))
info={}
for m,seeds in SEEDS.items():
  for sd in seeds:
    x,y=sd[0],sd[1]; box=sd[2] if len(sd)>2 else None
    l=lab[y,x]
    if l==0:
      d,ind=ndi.distance_transform_edt(lab==0,return_indices=True); l=lab[ind[0][y,x],ind[1][y,x]]
    reg=ndi.binary_dilation(lab==l,iterations=8)&free
    area=reg.sum(); info[(m,x,y)]=int(area)
    if box is not None:
      bm=np.zeros_like(reg); bm[box[1]:box[3],box[0]:box[2]]=True; reg=reg&bm
    elif area>120000: continue
    reg=ndi.binary_dilation(reg,iterations=4)&fg&(lum<185)|reg   # cover the line half
    idm[reg]=MUS.index(m); st[reg]=1
for k,v in info.items(): print(k,v)
st=ndi.gaussian_filter(st,1.2)
Image.fromarray(np.dstack([(idm/15*255).round(),st*255,np.zeros((H,W))]).astype(np.uint8)).save('mus.png')
v=im.copy().astype(float); v[st>0.3]=v[st>0.3]*0.4+np.array([0,255,90])*0.6
Image.fromarray(v.astype(np.uint8)).crop((300,500,1400,1900)).resize((550,700)).save('mus_viz.png')

# --- shape-limited light regions for pecs / delts / abs (overrides) ---
light=fg&(lum>=185)
light=ndi.binary_opening(light,iterations=2)
yy,xx=np.mgrid[0:H,0:W]
def ell(cx,cy,rx,ry): 
  r=np.sqrt(((xx-cx)/rx)**2+((yy-cy)/ry)**2); return np.clip((1.0-r)/0.12,0,1)
def put(name,shape):
  m=(light*shape)
  m=np.maximum(m, ndi.binary_dilation(m>0.5,iterations=3)*shape*0)  
  sel=m>st
  idm[sel]=MUS.index(name); st[sel]=m[sel]
idm[:]=0; st[:]=0
# re-add flood results for biceps/quads
for m_,seeds in (('biceps',SEEDS['biceps']),('quads',SEEDS['quads'])):
  for sd in seeds:
    x,y=sd[0],sd[1]; l=lab[y,x]
    if l==0:
      d,ind=ndi.distance_transform_edt(lab==0,return_indices=True); l=lab[ind[0][y,x],ind[1][y,x]]
    reg=ndi.binary_dilation(ndi.binary_dilation(lab==l,iterations=8)&free,iterations=3)&fg
    idm[reg]=MUS.index(m_); st[reg]=1
put('pecs',np.maximum(ell(725,690,135,92),ell(975,690,135,92)))
put('delts',np.maximum(ell(505,650,90,125),ell(1195,650,90,125)))
bx=np.zeros((H,W),bool); bx[838:1000,745:955]=True
ll,_=ndi.label(ndi.binary_erosion(light&bx,iterations=2))
absm=np.zeros((H,W),bool)
for (x,y) in [(805,875),(900,875),(805,955),(900,955)]:
  l=ll[y,x]
  if l==0:
    d,ind=ndi.distance_transform_edt(ll==0,return_indices=True); l=ll[ind[0][y,x],ind[1][y,x]]
  absm|=(ll==l)
absm=ndi.binary_dilation(absm,iterations=3)&fg
sel=absm; idm[sel]=MUS.index('abs'); st[sel]=1
st=ndi.gaussian_filter(st.astype(float),1.0)
Image.fromarray(np.dstack([(idm/15*255).round(),np.clip(st,0,1)*255,np.zeros((H,W))]).astype(np.uint8)).save('mus.png')
v=im.copy().astype(float); a=np.clip(st,0,1)[...,None]*0.65; v=v*(1-a)+np.array([0,255,90])*a
Image.fromarray(v.astype(np.uint8)).crop((300,500,1400,1900)).resize((550,700)).save('mus_viz.png')
