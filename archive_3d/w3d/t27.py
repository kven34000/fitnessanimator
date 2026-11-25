import asyncio
from drv import Eng
from PIL import Image
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  ims=[]
  for ol in [0.0014,0.0]:
    st={'t':0.4,'cam':{'pos':[0,1.3,0.9],'target':[0,1.2,0],'fov':30},'outline':ol,'charRotY':0.1,'clips':[{'name':'AirSquat','time':0.0}],'muscles':{},'fingerCurl':0.3}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=92)
    ims.append(Image.open('/tmp/a.jpg').crop((560,240,1360,840)))
  o=Image.new('RGB',(1600,600))
  for i,im in enumerate(ims): o.paste(im,(i*800,0))
  o.save('chest2.png'); await e.stop()
asyncio.run(main())
