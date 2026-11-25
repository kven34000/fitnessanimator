import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Idle','Flex','MutantFlex','Stairs','ThumbsUp','Point']:
    print(n, await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')"))
  cam={'pos':[0,1.0,4.2],'target':[0,0.95,0],'fov':30}
  shots=[('rest',[],0),('sq1','AirSquat',0.6),('sq2','AirSquat',1.0),('idle','Idle',1.0),('flex','Flex',1.6),('mflex','MutantFlex',2.5),('thumb','ThumbsUp',2.0),('point','Point',1.2),('stairs','Stairs',0.3)]
  ims=[]
  for nm,clip,t in shots:
    st={'t':0,'cam':cam,'outline':0.0014,'charRotY':0.35,'clips':[{'name':clip,'time':t}] if clip else []}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=80)
    im=Image.open('/tmp/a.jpg').crop((560,0,1360,1080)).resize((320,432)); ImageDraw.Draw(im).text((4,4),nm,fill='yellow'); ims.append(im)
  o=Image.new('RGB',(320*5,432*2))
  for i,im in enumerate(ims): o.paste(im,((i%5)*320,(i//5)*432))
  o.save('mx_grid.png')
  print('shorts',await e.ev("()=>window._shortsTris"))
  await e.stop()
asyncio.run(main())
