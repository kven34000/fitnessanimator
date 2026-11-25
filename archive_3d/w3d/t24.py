import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Idle','Flex','Point']: await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')")
  ims=[]
  for nm,clip,t,ry,b in [('idle','Idle',1.0,0.3,'mixamorigLeftHand'),('point','Point',0.8,0.0,'mixamorigLeftHand'),('flex','Flex',2.0,0.0,'mixamorigRightHand'),('sq','AirSquat',0.9,0.6,'mixamorigLeftHand')]:
    st={'t':0,'cam':{'pos':[0,1.0,4],'target':[0,1,0],'fov':30},'outline':0.0014,'charRotY':ry,'clips':[{'name':clip,'time':t}]}
    await e.pg.evaluate('(s)=>window.frame(s)',st)
    p=await e.ev(f"()=>window.boneWorld('{b}')")
    st['cam']={'pos':[p[0]+0.05,p[1]+0.05,p[2]+0.6],'target':p,'fov':30}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=85)
    im=Image.open('/tmp/a.jpg').crop((660,240,1260,840)).resize((400,400)); ImageDraw.Draw(im).text((4,4),nm,fill='yellow'); ims.append(im)
  o=Image.new('RGB',(1600,400))
  for i,im in enumerate(ims): o.paste(im,(i*400,0))
  o.save('hands2.png'); await e.stop()
asyncio.run(main())
