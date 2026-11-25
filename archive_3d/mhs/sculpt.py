# muscle definition + per-muscle masks on T-posed MH body
import bpy, numpy as np, sys, json
J=json.load(open('/home/claude/mhs/joints.json'))
MUS=['pecs','abs','obliques','delts','biceps','triceps','forearms','lats','traps','quads','hams','glutes','calves','lowback','serratus','spare']
def ss(a,b,x):
  t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def sculpt(h, strength=1.0):
  me=h.data; n=len(me.vertices)
  co=np.array([v.co[:] for v in me.vertices]); nor=np.array([v.normal[:] for v in me.vertices])
  x,y,z=co[:,0],co[:,1],co[:,2]; S=np.sign(x)+(x==0); ax=np.abs(x)
  M={k:np.zeros(n) for k in MUS}; D=np.zeros(n); INK=np.zeros(n)
  def add(name,inside,disp,edge=None,inkw=1.0):
    M[name]=np.maximum(M[name],inside)
    nonlocal D, INK
    D=D+disp*inside
    if edge is not None: INK=np.maximum(INK,edge*inkw)
  def blob(r,soft=0.12):  # r: normalized radius -> inside, edge
    inside=1-ss(1-soft,1.0,r); edge=np.exp(-((r-1.0)/0.07)**2)
    return inside,edge
  front=nor[:,1]<-0.25; back=nor[:,1]>0.25
  torso=(z>0.9)&(z<1.6)&(ax<0.24)
  # pecs
  u=(ax-0.105*J['LeftArm'][0]/0.229*0.92)/(0.105*J['LeftArm'][0]/0.229*0.95); v=(z-1.36)/np.where(z<1.36,0.075,0.10)
  r=(np.abs(u)**3.2+np.abs(v)**3.2)**(1/3.2)
  i,e=blob(r,0.25); m=(torso&(y<-0.02)&(ax>0.006)).astype(float)
  add('pecs',i*m,0.012,e*m*(z<1.38))
  # abs grid
  rows=[(1.205,1.272),(1.135,1.197),(1.065,1.127),(0.975,1.057)]
  for (z0,z1) in rows:
    cx=(0.014+0.062)/2; cz=(z0+z1)/2; hx=(0.062-0.014)/2; hz=(z1-z0)/2
    du=np.abs(ax-cx)/hx; dv=np.abs(z-cz)/hz
    r=(du**4+dv**4)**0.25
    i,e=blob(r,0.22); m=(torso&front&(ax<0.09)).astype(float)
    add('abs',i*m,0.007,e*m)
  # obliques
  u=(ax-0.115)/0.05; v=(z-1.08)/0.12; r=np.sqrt(u*u+v*v)
  i,e=blob(r,0.3); m=(torso&(y<0.03)).astype(float); add('obliques',i*m,0.004,e*m,0.6)
  # serratus (3 fingers under pec side)
  for k,zc in enumerate([1.31,1.255,1.20]):
    u=(ax-0.165+k*0.005)/0.03; v=(z-zc)/0.022; r=np.sqrt(u*u+v*v)
    i,e=blob(r,0.3); m=(torso&(y<0.02)).astype(float); add('serratus',i*m,0.004,e*m,0.6)
  # lats
  u=(ax-0.14)/0.08; v=(z-1.30)/0.13; r=np.sqrt(u*u+v*v); i,e=blob(r,0.35)
  m=(torso&(y>-0.02)).astype(float); add('lats',i*m,0.007,e*m,0.4)
  # traps
  u=(ax-0.09)/0.09; v=(z-1.55)/0.06; r=np.sqrt(u*u+v*v); i,e=blob(r,0.35)
  m=((z>1.45)&(z<1.68)&(y>-0.06)&(ax<0.22)).astype(float); add('traps',i*m,0.008,e*m*(y>0),0.5)
  # lower back erectors
  u=(ax-0.035)/0.03; v=(z-1.10)/0.11; r=np.sqrt(u*u+v*v); i,e=blob(r,0.3)
  m=(torso&back).astype(float); add('lowback',i*m,0.005,e*m,0.6)
  # glutes
  u=(ax-0.085)/0.085; v=(z-0.93)/0.09; r=np.sqrt(u*u+v*v); i,e=blob(r,0.3)
  m=((z>0.8)&(z<1.06)&(y>0.0)).astype(float); add('glutes',i*m,0.008,e*m,0.5)
  # limbs: local coords along bone
  def limb(p0,p1,sel):
    # slice-centroid local frame; axis 0=x (arms) or 2=z (legs)
    p0=np.array(p0);p1=np.array(p1)
    k=0 if abs(p1[0]-p0[0])>abs(p1[2]-p0[2]) else 2
    coord=ax if k==0 else z
    t=(coord-p0[k])/(p1[k]-p0[k])
    perp=np.zeros((n,3)); idx=np.nonzero(sel&(x>0))[0]
    lo,hi=min(p0[k],p1[k])-0.05,max(p0[k],p1[k])+0.05
    bins=np.linspace(lo,hi,22); cen={}
    q=np.stack([ax,y,z],1)
    for b0,b1 in zip(bins[:-1],bins[1:]):
      m=sel&(coord>=b0)&(coord<b1)&(x>0)
      if m.sum()>5: cen[(b0+b1)/2]=q[m].mean(0)
    keys=np.array(sorted(cen)); C=np.array([cen[c] for c in keys])
    for _ in range(3): C[1:-1]=(C[:-2]+2*C[1:-1]+C[2:])/4
    cc=np.stack([np.interp(coord,keys,C[:,j]) for j in range(3)],1)
    perp=q-cc; perp[:,k]=0
    return t,perp
  # arms (left, mirrored)
  arm=(ax>J['LeftArm'][0]-0.03)&(z>1.38)&(z<1.56)
  t,p=limb(J['LeftArm'],J['LeftForeArm'],arm)
  fw=-p[:,1]; up=p[:,2]
  def ell(t0,tr,a0,ar,b0,br,a,b,tt): return np.sqrt(((tt-t0)/tr)**2+((a-a0)/ar)**2+((b-b0)/br)**2)
  r=ell(0.55,0.42,0.04,0.035,0.0,0.05,fw,up,t); i,e=blob(r,0.3); m=(arm&(t>0)&(t<1)&(fw>0)).astype(float); add('biceps',i*m,0.013,e*m*(fw>0.02),0.35)
  r=ell(0.45,0.5,-0.035,0.035,0.01,0.05,fw,up,t); i,e=blob(r,0.3); m=(arm&(t>0)&(t<1)&(fw<0)).astype(float); add('triceps',i*m,0.009,None)
  r=ell(0.02,0.22,0.0,0.07,0.03,0.06,fw,up,t); i,e=blob(r,0.3); m=(arm&(t<0.3)&(up>-0.02)).astype(float); add('delts',i*m,0.012,e*m,0.3)
  t2,p2=limb(J['LeftForeArm'],J['LeftHand'],arm); fw2=-p2[:,1]; up2=p2[:,2]
  r=ell(0.3,0.38,0.01,0.045,0.02,0.04,fw2,up2,t2); i,e=blob(r,0.35); m=(arm&(t2>0)&(t2<0.9)).astype(float); add('forearms',i*m,0.006,None)
  # legs
  leg=(z<0.95)&(ax>0.03)
  t,p=limb(J['LeftUpLeg'],J['LeftLeg'],leg); fw=-p[:,1]; out=p[:,0]
  thigh=leg&(t>0)&(t<1.05)
  r=ell(0.5,0.5,0.075,0.06,0.0,0.06,fw,out,t); i,e=blob(r,0.3); m=(thigh&(fw>0)).astype(float); add('quads',i*m,0.010,e*m,0.4)
  r=ell(0.5,0.4,0.03,0.05,0.07,0.04,fw,out,t); i,e=blob(r,0.3); m=(thigh&(out>0)).astype(float); add('quads',i*m,0.008,e*m,0.3)
  r=ell(0.85,0.15,0.045,0.04,-0.05,0.04,fw,out,t); i,e=blob(r,0.3); m=(thigh&(out<0)).astype(float); add('quads',i*m,0.010,e*m,0.4)
  r=ell(0.5,0.42,-0.07,0.05,0.0,0.06,fw,out,t); i,e=blob(r,0.3); m=(thigh&(fw<0)).astype(float); add('hams',i*m,0.007,e*m,0.3)
  t,p=limb(J['LeftLeg'],J['LeftFoot'],leg); fw=-p[:,1]; out=p[:,0]
  shin=leg&(t>0)&(t<1)
  for o in (0.022,-0.022):
    r=ell(0.28,0.2,-0.055,0.04,o*1.3,0.035,fw,out,t); i,e=blob(r,0.3); m=(shin&(fw<0.01)).astype(float); add('calves',i*m,0.012,e*m,0.4)
  D=D*strength - INK*0.0025
  co2=co+nor*D[:,None]
  for k,vv in enumerate(me.vertices): vv.co=co2[k]
  me.update()
  def colattr(name,arr4):
    a=me.color_attributes.new(name=name,type='FLOAT_COLOR',domain='POINT')
    a.data.foreach_set('color',np.clip(arr4,0,1).astype(np.float32).ravel())
  for gi_,nm in enumerate(['_MA','_MB','_MC','_MD']):
    colattr(nm,np.stack([M[MUS[gi_*4+j]] for j in range(4)],1))
  colattr('_INK',np.stack([INK,INK,INK,np.ones(n)],1))
  return M,INK
