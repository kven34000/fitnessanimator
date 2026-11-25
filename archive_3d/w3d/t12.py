import asyncio
from drv import Eng
async def main():
  e=await Eng().start()
  for n in ['87_02','79_94']: await e.ev(f"()=>window.loadBVH('{n}','bvh/{n}.bvh')")
  cam={'pos':[0,1.45,1.6],'target':[0,1.35,0],'fov':30}
  await e.shot({'t':0,'cam':cam},'h_rest.jpg',70)
  await e.shot({'t':0,'anim':{'name':'87_02','time':0.5,'t0':0.5},'cam':cam},'h_t.jpg',70)
  await e.shot({'t':0,'anim':{'name':'79_94','time':2.0,'t0':0},'cam':cam},'h_f.jpg',70)
  await e.shot({'t':0,'anim':{'name':'79_94','time':2.0,'t0':0},'cam':{'pos':[2.0,1.45,0.2],'target':[0,1.35,0],'fov':30}},'h_fs.jpg',70)
  await e.stop()
asyncio.run(main())
