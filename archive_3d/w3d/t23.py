import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def strip(e,clip,times,name):
  ims=[]
  for t in times:
    st={'t':0,'cam':{'pos':[0,1.0,4.2],'target':[0,0.95,0],'fov':30},'outline':0.0014,'charRotY':0.2,'clips':[{'name':clip,'time':t}]}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=60)
    im=Image.open('/tmp/a.jpg').crop((560,0,1360,1080)).resize((160,216)); ImageDraw.Draw(im).text((3,3),f'{t:.1f}',fill='yellow'); ims.append(im)
  o=Image.new('RGB',(160*len(ims),216))
  for i,im in enumerate(ims): o.paste(im,(i*160,0))
  o.save(name)
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Flex','MutantFlex','Point','ThumbsUp','Idle']: await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')")
  await strip(e,'Flex',[0.3*i for i in range(13)],'s_flex.jpg')
  await strip(e,'MutantFlex',[0.36*i for i in range(13)],'s_mflex.jpg')
  await strip(e,'Point',[0.16*i for i in range(13)],'s_point.jpg')
  await strip(e,'ThumbsUp',[0.33*i for i in range(13)],'s_thumb.jpg')
  await strip(e,'AirSquat',[0.15*i for i in range(13)],'s_sq.jpg')
  await e.stop()
asyncio.run(main())
