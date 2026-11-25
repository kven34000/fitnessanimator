import asyncio
from drv import Eng
from PIL import Image
PRE="()=>{window.MODEL='mh_AirSquat.glb';window.SH_HEM=0.80/1.8;window.SH_WAIST=0.965/1.8;}"
async def main():
  e=Eng(None,'engine3.html',PRE); await e.start()
  print(await e.ev("()=>window._shortsTris"))
  ims=[]
  for t,cp in [(0.0,[0,1.0,-2.4]),(0.0,[2.4,1.0,0])]:
    st={'t':0.4,'cam':{'pos':cp,'target':[0,0.9,0],'fov':35},'charRotY':0,'clips':[{'name':'AirSquat','time':t}],'muscles':{},'fingers':'anim'}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=90)
    ims.append(Image.open('/tmp/a.jpg').crop((660,240,1260,840)))
  o=Image.new('RGB',(1200,600))
  for i,im in enumerate(ims): o.paste(im,(i*600,0))
  o.save('mh3.png'); await e.stop()
asyncio.run(main())
