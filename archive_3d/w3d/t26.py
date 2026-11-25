import asyncio
from drv import Eng
from PIL import Image
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Flex','Idle']: await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')")
  ims=[]
  for clip,t,mus in [('Idle',1.0,{}),('Flex',2.0,{}),('Flex',2.0,{'pecs':1,'abs':1})]:
    st={'t':0.4,'cam':{'pos':[0,1.35,1.3],'target':[0,1.25,0],'fov':30},'outline':0.0014,'charRotY':0.1,'clips':[{'name':clip,'time':t}],'muscles':mus,'fingerCurl':0.3}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=90)
    ims.append(Image.open('/tmp/a.jpg').crop((560,140,1360,940)).resize((480,480)))
  o=Image.new('RGB',(1440,480))
  for i,im in enumerate(ims): o.paste(im,(i*480,0))
  o.save('chest.png'); await e.stop()
asyncio.run(main())
