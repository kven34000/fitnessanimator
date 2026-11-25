import asyncio
from drv import Eng
from PIL import Image
PRE="()=>{window.MODEL='mh_AirSquat.glb';window.SH_HEM=0.765/1.8;window.SH_WAIST=0.99/1.8;}"
V=[ # name, clip,time, cam pos, target, extra
 ('full','Idle',1.0,[0,1.0,3.6],[0,0.92,0],{}),
 ('torso','Idle',1.0,[0.5,1.35,1.5],[0,1.25,0],{}),
 ('back','Idle',1.0,[-0.6,1.35,-1.7],[0,1.2,0],{}),
 ('abs_glow','Idle',1.0,[0.5,1.35,1.5],[0,1.25,0],{'muscles':{'abs':1}}),
 ('squat','AirSquat',0.9,[1.4,1.1,2.4],[0,0.7,0],{'muscles':{'quads':1,'glutes':1}}),
 ('flex','MutantFlex',1.9,[0,1.3,2.4],[0,1.1,0],{'muscles':{'biceps':1,'pecs':1}}),
]
async def main():
  e=Eng(None,'engine3.html',PRE); await e.start()
  for n in ['Idle','MutantFlex']: await e.ev(f"()=>window.loadClip('{n}','mh_{n}.glb')")
  ims=[]
  for nm,clip,t,cp,ct,ex in V:
    st={'t':0.4,'cam':{'pos':cp,'target':ct,'fov':35},'charRotY':0,'clips':[{'name':clip,'time':t}],'muscles':{},'fingers':'anim','outline':0.0012}
    st.update(ex)
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=90)
    ims.append(Image.open('/tmp/a.jpg').crop((420,0,1500,1080)).resize((540,540)))
  o=Image.new('RGB',(1620,1080))
  for i,im in enumerate(ims): o.paste(im,((i%3)*540,(i//3)*540))
  o.save('mh4.png'); await e.stop()
asyncio.run(main())
