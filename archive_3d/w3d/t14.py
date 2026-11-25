import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def strip(e, clip, times, ry, name, cam):
  ims=[]
  for t in times:
    await e.pg.evaluate('(s)=>window.frame(s)',{'t':0,'anim':{'name':clip,'time':t,'t0':times[0]},'charRotY':ry,'cam':cam})
    await e.pg.screenshot(path='/tmp/x.jpg',type='jpeg',quality=60)
    ims.append(Image.open('/tmp/x.jpg').crop((560,0,1360,1080)).resize((160,216)))
  o=Image.new('RGB',(160*len(ims),216))
  for i,im in enumerate(ims): o.paste(im,(i*160,0)); ImageDraw.Draw(o).text((i*160+3,3),f'{times[i]:.1f}',fill='yellow')
  o.save(name)
async def main():
  e=await Eng('tex_clean.jpg').start()
  for n in ['13_29','14_06','22_14','79_94','13_27','82_08','86_02']: await e.ev(f"()=>window.loadBVH('{n}','bvh/{n}.bvh')")
  cam={'pos':[0,1.0,4.5],'target':[0,0.9,0],'fov':30}
  await strip(e,'13_29',[31.5+0.4*i for i in range(16)],0.9,'s_13_29.jpg',cam)
  await strip(e,'14_06',[9.0+0.3*i for i in range(14)],0.9,'s_14_06.jpg',cam)
  await strip(e,'22_14',[0.5+0.35*i for i in range(14)],0.9,'s_22_14.jpg',cam)
  await strip(e,'79_94',[0.0+0.5*i for i in range(16)],0.0,'s_79_94.jpg',cam)
  await strip(e,'13_27',[0.0+2.0*i for i in range(17)],0.0,'s_13_27.jpg',cam)
  await e.stop()
asyncio.run(main())
