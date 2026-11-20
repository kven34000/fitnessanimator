import asyncio, json, math, sys, io, base64, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0,'/home/claude/w3d')
from playwright.async_api import async_playwright
import render3d as RD
from drv import ARGS
P=json.load(open('/home/claude/p2d/keys.json')); KEYS=P['keys']; BONES=P['bones']
CHILD={}
for i,(a,b) in enumerate(BONES): CHILD.setdefault(a,[]).append((i,b))
def ang(v): return math.atan2(v[1],v[0])
def rot(a): c,s=math.cos(a),math.sin(a); return np.array([[c,-s],[s,c]])
def skel(J): return {b:(ang(np.subtract(J[b],J[a])),np.hypot(*np.subtract(J[b],J[a]))) for a,b in BONES}
JK={}
for kk in KEYS: JK[kk['k']]=kk['J']
SK=[skel(JK[i]) for i in range(len(JK))]
def target(A,B,u):
  # interpolated joints, root ankle at origin
  pos={'ank':np.zeros(2)}
  def walk(j):
    for i,c in CHILD.get(j,[]):
      ta,la=SK[A][c]; tb,lb=SK[B][c]
      d=(tb-ta+math.pi)%(2*math.pi)-math.pi
      th=ta+d*u; L=la+(lb-la)*u
      pos[c]=pos[j]+L*np.array([math.cos(th),math.sin(th)]); walk(c)
  walk('ank'); return pos
def warp(L,pos):
  J=L['J']; V=np.array(L['verts']); bi=np.array(L['bi']); bw=np.array(L['bw'])
  Ms=[];St=[];R0=[]
  for a,b in BONES:
    r=np.subtract(J[b],J[a]); t=pos[b]-pos[a]
    M=rot(ang(t))@np.diag([np.hypot(*t)/max(np.hypot(*r),1e-6),1.0])@rot(-ang(r))
    Ms.append(M); St.append(pos[a]); R0.append(np.array(J[a],float))
  Ms=np.array(Ms);St=np.array(St);R0=np.array(R0)
  out=np.zeros_like(V)
  for c in range(bi.shape[1]):
    idx=bi[:,c]; out+=bw[:,c:c+1]*(St[idx]+np.einsum('nij,nj->ni',Ms[idx],V-R0[idx]))
  return out
def sm(x): x=min(1,max(0,x)); return x*x*(3-2*x)
# timeline: rep = down 0->3 (0.9s), hold 0.2, up 3->0 (0.8), hold 0.15
REP=[(0.0,0.3,0,1),(0.3,0.6,1,2),(0.6,0.9,2,3),(0.9,1.1,3,3),(1.1,1.37,3,2),(1.37,1.64,2,1),(1.64,1.9,1,0),(1.9,2.05,0,0)]
RL=2.05
def state(t):
  tt=t%RL
  for a,b,A,B in REP:
    if a<=tt<b: u=sm((tt-a)/(b-a)); return A,B,u,int(t//RL)
  return 0,0,0,int(t//RL)
async def main(t0,t1,out,stills=None):
  pw=await async_playwright().start(); br=await pw.chromium.launch(executable_path='/usr/bin/google-chrome',args=ARGS)
  pg=await br.new_page(viewport={'width':1920,'height':1080}); pg.on('pageerror',lambda e:print('PAGEERR',e))
  await pg.goto('file:///home/claude/p2d/kf.html'); await pg.wait_for_function('window.ready===true')
  await pg.evaluate('(p)=>window.init(p)',{'W':P['W'],'H':P['H'],'layers':[{'name':k['name'],'tex':k['tex'],'mus':'mus_key.png','verts':k['verts'],'tris':k['tris']} for k in KEYS]})
  bgp=await br.new_page(viewport={'width':1920,'height':1080})
  await bgp.goto('file:///home/claude/w3d/engine3.html'); await bgp.wait_for_function('window.ready===true')
  await bgp.evaluate("()=>{window.MODEL='mh_AirSquat.glb';}"); await bgp.evaluate('()=>window.load(null)')
  CAM={'pos':[0,0.95,3.7],'target':[0,0.92,0],'fov':30}
  gp=await bgp.evaluate('(c)=>{window.frame({t:0,char:false,cam:c,clips:[{name:"AirSquat",time:0}]});return window.projPts([[0,0,0]]);}',CAM)
  ground=np.array([985.0,1000.0]); k=0.6
  ff=None
  if out: ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
  times=stills or [i/30 for i in range(int(t0*30),int(t1*30))]
  for t in times:
    A,B,u,rep=state(t)
    pos=target(A,B,u)
    lay={}; op={}; order=[]
    wB=sm((u-0.3)/0.4) if A!=B else 0.0
    for ii,(kk,w) in enumerate(((A,1.0),(B,wB))):
      if ii==1 and (A==B or w<=0.001): continue
      for L in KEYS:
        if L['k']!=kk: continue
        scr=ground+warp(L,pos)*k
        lay[L['name']]=scr.ravel().round(2).tolist(); op[L['name']]=w; order.append(L['name'])
    await pg.evaluate('(f)=>window.draw(f)',{'layers':lay,'order':order,'op':op,'t':t,'w':[0]*16})
    fg=Image.open(io.BytesIO(base64.b64decode((await pg.evaluate('()=>window.grab()')).split(',')[1]))).convert('RGBA')
    await bgp.evaluate('(s)=>window.frame(s)',{'t':t,'char':False,'cam':CAM,'clips':[{'name':'AirSquat','time':0}]})
    bg=Image.open(io.BytesIO(base64.b64decode((await bgp.evaluate('()=>window.grab()')).split(',')[1]))).convert('RGBA')
    bg.alpha_composite(fg)
    if ff: ff.stdin.write(bg.convert('RGB').tobytes())
    else: bg.convert('RGB').save(f'/home/claude/p2d/k_{t}.jpg',quality=88)
  if ff: ff.stdin.close(); ff.wait()
  await br.close(); await pw.stop()
if __name__=='__main__':
  if sys.argv[1]=='stills': asyncio.run(main(0,0,None,[float(x) for x in sys.argv[2:]]))
  else: asyncio.run(main(float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]))
