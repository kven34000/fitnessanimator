import asyncio,sys
from drv import Eng
from PIL import Image
PRE="()=>{window.MODEL='mh_AirSquat.glb';window.SH_HEM=0.80/1.8;window.SH_WAIST=0.965/1.8;}"
async def main():
  e=Eng(None,'engine3.html',PRE); await e.start(); print('bones',e.bones)
  for n in ['Flex','Idle']: await e.ev(f"()=>window.loadClip('{n}','mh_{n}.glb')")
  ims=[]
  shots=[('Idle',1.0,{},0.3,[0,1.0,3.4],[0,0.95,0]),('AirSquat',0.9,{'quads':1,'glutes':1},0.6,[2.2,1.0,2.6],[0,0.7,0]),
         ('Flex',2.0,{'pecs':1,'abs':1,'biceps':1},0.2,[0,1.4,1.6],[0,1.25,0]),('Idle',1.0,{'abs':1},0.0,[0,1.25,1.0],[0,1.2,0])]
  for clip,t,mus,ry,cp,ct in shots:
    st={'t':0.4,'cam':{'pos':cp,'target':ct,'fov':35},'charRotY':ry,'clips':[{'name':clip,'time':t}],'muscles':mus,'fingers':'anim'}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=90)
    ims.append(Image.open('/tmp/a.jpg').crop((420,0,1500,1080)).resize((540,540)))
  o=Image.new('RGB',(2160,540))
  for i,im in enumerate(ims): o.paste(im,(i*540,0))
  o.save('mh1.png'); await e.stop()
asyncio.run(main())
