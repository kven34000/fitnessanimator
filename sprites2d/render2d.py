import asyncio, json, math, sys, io, base64, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0,'/home/claude/w3d')
from playwright.async_api import async_playwright
import render10c as R, render3d as RD
R.SEGS[2]=(5.64,7.45,'Flex',1.2,False)
from drv import ARGS
P=json.load(open('/home/claude/p2d/puppet.json')); JS=json.load(open('/home/claude/p2d/joints10.json'))
J={k:np.array(v,float) for k,v in P['joints'].items()}; BONES=P['bones']; names=P['names']
MUS=['pecs','abs','obliques','delts','biceps','triceps','forearms','lats','traps','quads','hams','glutes','calves','lowback','serratus','spare']
M3={'spineLow':('Hips','Spine2'),'spineUp':('Spine2','Neck'),'head':('Head','HeadTop_End')}
for S,SS in (('R','Right'),('L','Left')):
  M3.update({f'{S}_clav':('Spine2',f'{SS}Arm'),f'{S}_up':(f'{SS}Arm',f'{SS}ForeArm'),f'{S}_fore':(f'{SS}ForeArm',f'{SS}Hand'),f'{S}_hand':(f'{SS}Hand',f'{SS}HandMiddle4'),
    f'{S}_pel':('Hips',f'{SS}UpLeg'),f'{S}_thigh':(f'{SS}UpLeg',f'{SS}Leg'),f'{S}_shin':(f'{SS}Leg',f'{SS}Foot'),f'{S}_foot':(f'{SS}Foot',f'{SS}Toe_End')})
NOSCALE={'head','R_hand','L_hand','R_foot','L_foot'}
YAW=[0.0]
def g(fr,n):
  v=np.array(fr['mixamorig'+n]); c,s=math.cos(YAW[0]),math.sin(YAW[0]); return np.array([c*v[0]+s*v[2],v[1],-s*v[0]+c*v[2]])
def p2(v): return np.array([v[0],-v[1]])
rest=JS['rest']
s_draw=np.linalg.norm(J['R_hip']-J['R_ank'])/np.linalg.norm(p2(g(rest,'RightUpLeg')-g(rest,'RightFoot')))
order_b=[]  # hierarchical order
def add(b):
  if b in order_b: return
  par=BONES[b][3]
  if par: add(par)
  order_b.append(b)
for b in names: add(b)
def ang(v): return math.atan2(v[1],v[0])
def rot(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s],[s,c]])
def pose(fr):
  jp={'pelvis':J['pelvis']+(p2(g(fr,'Hips'))-p2(g(rest,'Hips')))*s_draw}
  A={}
  for b in order_b:
    j0,j1,ly,par=BONES[b]
    a3,b3=M3[b]
    vr=p2(g(rest,b3)-g(rest,a3)); vt=p2(g(fr,b3)-g(fr,a3))
    fr_r=np.linalg.norm(vr)/np.linalg.norm(g(rest,b3)-g(rest,a3)); fr_t=np.linalg.norm(vt)/max(1e-6,np.linalg.norm(g(fr,b3)-g(fr,a3)))
    sx=1.0 if b in NOSCALE else max(0.5,fr_t/max(fr_r,1e-3))
    r2=J[j1]-J[j0]; th0=ang(r2); dth=ang(vt)-ang(vr)
    M=rot(th0+dth)@np.diag([sx,1.0])@rot(-th0)
    st=jp[j0]
    A[b]=(M,st,J[j0])
    jp[j1]=st+M@r2
  return A,jp
async def main(t0,t1,out,stills=None):
  pw=await async_playwright().start(); br=await pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=ARGS)
  pg=await br.new_page(viewport={'width':1920,'height':1080}); pg.on('pageerror',lambda e:print('PAGEERR',e))
  await pg.goto('file:///home/claude/p2d/puppet.html'); await pg.wait_for_function('window.ready===true')
  await pg.evaluate('(p)=>window.init(p)',{'W':P['W'],'H':P['H'],'layers':[{k:l[k] for k in ('name','tex','verts','tris')} for l in P['layers']]})
  bgp=await br.new_page(viewport={'width':1920,'height':1080})
  await bgp.goto('file:///home/claude/w3d/engine3.html'); await bgp.wait_for_function('window.ready===true')
  await bgp.evaluate("()=>{window.MODEL='mh_AirSquat.glb';}"); await bgp.evaluate('()=>window.load(null)')
  CAM={'pos':[0,0.95,3.7],'target':[0,0.92,0],'fov':30}
  gp=await bgp.evaluate('(c)=>{window.frame({t:0,char:false,cam:c,clips:[{name:"AirSquat",time:0}]});return window.projPts([[0,0,0],[0,1.85,0]]);}',CAM)
  ground=np.array(gp[0]); pxm=gp[0][1]-gp[1][1]  # screen px for 1.85 m
  sole=np.array([850,2470.]); k=pxm/(2470-40)
  LY={l['name']:(np.array(l['verts']),np.array(l['bi']),np.array(l['bw'])) for l in P['layers']}
  ff=None
  if out: ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
  times=stills or [i/30 for i in range(int(t0*30),int(t1*30))]
  for t in times:
    fi=str(min(int(round(t*30)),len(JS['frames'])-1)); fr=JS['frames'][fi]
    st,ov=R.state(t)
    YAW[0]=0.0 if t>=3.6 else math.radians(0)*min(1,t/0.3) if t<3.3 else math.radians(0)*(3.6-t)/0.3
    A,jp=pose(fr)
    Ms=np.stack([A[b][0] for b in names]); St=np.stack([A[b][1] for b in names]); Rj=np.stack([A[b][2] for b in names])
    lay={}
    for nm,(V,bi,bw) in LY.items():
      out_=np.zeros_like(V)
      for c in range(bi.shape[1]):
        idx=bi[:,c]; d=V-Rj[idx]
        out_+=bw[:,c:c+1]*(St[idx]+np.einsum('nij,nj->ni',Ms[idx],d))
      scr=ground+(out_-sole)*k
      lay[nm]=scr.ravel().round(2).tolist()
    # arm behind body?
    zc=g(fr,'Spine2')[2]
    armsBack=[s for s,SS in (('R','Right'),('L','Left')) if g(fr,SS+'Hand')[2]<zc-0.12]
    order=[l for l in ('legR','legL') ]+[ 'arm'+s for s in armsBack]+['body']+['arm'+s for s in 'RL' if s not in armsBack]
    w=[float(st['muscles'].get(m,0)) for m in MUS]
    await pg.evaluate('(f)=>window.draw(f)',{'layers':lay,'order':order,'w':w,'t':t})
    fg=Image.open(io.BytesIO(base64.b64decode((await pg.evaluate('()=>window.grab()')).split(',')[1]))).convert('RGBA')
    bst={'t':t,'char':False,'cam':CAM,'clips':[{'name':'AirSquat','time':0}],'props':st['props'],'project':st['project']}
    proj=await bgp.evaluate('(s)=>window.frame(s)',bst)
    bg=Image.open(io.BytesIO(base64.b64decode((await bgp.evaluate('()=>window.grab()')).split(',')[1]))).convert('RGBA')
    bg.alpha_composite(fg)
    RD.overlay(bg,t,ov,proj or {})
    if ff: ff.stdin.write(bg.convert('RGB').tobytes())
    else: bg.convert('RGB').save(f'/home/claude/p2d/s_{t}.jpg',quality=88)
  if ff: ff.stdin.close(); ff.wait()
  await br.close(); await pw.stop()
if __name__=='__main__':
  if sys.argv[1]=='stills': asyncio.run(main(0,0,None,[float(x) for x in sys.argv[2:]]))
  else: asyncio.run(main(float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]))
