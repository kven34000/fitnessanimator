import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Idle','Flex']: await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')")
  print('tris',await e.ev("()=>window._shortsTris"))
  ims=[]
  for nm,clip,t,ry,cam,mus in [('idle','Idle',1.0,0.3,([0,0.95,2.6],[0,0.85,0]),{}),('sq','AirSquat',1.0,0.7,([0,0.8,2.6],[0,0.6,0]),{'quads':1,'glutes':0.8}),
      ('sqb','AirSquat',1.0,2.8,([0,0.8,2.6],[0,0.6,0]),{'glutes':1,'hams':0.7}),('flex','Flex',1.6,0.0,([0,1.2,2.6],[0,1.1,0]),{'biceps':1,'pecs':0.6,'abs':0.6})]:
    st={'t':0.3,'cam':{'pos':cam[0],'target':cam[1],'fov':30},'outline':0.0014,'charRotY':ry,'clips':[{'name':clip,'time':t}],'muscles':mus}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=85)
    im=Image.open('/tmp/a.jpg').crop((420,0,1500,1080)).resize((480,480)); ImageDraw.Draw(im).text((4,4),nm,fill='yellow'); ims.append(im)
  o=Image.new('RGB',(480*4,480))
  for i,im in enumerate(ims): o.paste(im,(i*480,0))
  o.save('shorts2.png'); await e.stop()
asyncio.run(main())
