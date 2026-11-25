import asyncio
from drv import Eng
from PIL import Image
PRE="()=>{window.MODEL='mh_AirSquat.glb';window.SH_HEM=0.80/1.8;window.SH_WAIST=0.965/1.8;}"
async def main():
  e=Eng(None,'engine3.html',PRE); await e.start()
  ims=[]
  for t,mus,cp,ct in [(0.9,{'quads':1},[0.4,1.3,2.0],[0,0.6,0]),(0.9,{'glutes':1,'hams':1},[-1.6,1.0,-1.8],[0,0.7,0]),(0.0,{'quads':1,'calves':1},[1.2,0.8,2.0],[0,0.6,0])]:
    st={'t':0.4,'cam':{'pos':cp,'target':ct,'fov':35},'charRotY':0,'clips':[{'name':'AirSquat','time':t}],'muscles':mus,'fingers':'anim'}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=90)
    ims.append(Image.open('/tmp/a.jpg').crop((420,0,1500,1080)).resize((540,540)))
  o=Image.new('RGB',(1620,540))
  for i,im in enumerate(ims): o.paste(im,(i*540,0))
  o.save('mh2.png'); await e.stop()
asyncio.run(main())
