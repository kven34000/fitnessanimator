import asyncio
from drv import Eng
async def main():
  cams=[{'pos':[0,1.25,2.2],'target':[0,1.15,0],'fov':30},{'pos':[0,1.0,4.3],'target':[0,0.95,0],'fov':30}]
  e=await Eng().start()
  await e.ev("()=>window.loadBVH('79_94','bvh/79_94.bvh')")
  for i,c in enumerate(cams): await e.shot({'t':0,'anim':{'name':'79_94','time':2.0,'t0':0},'cam':c,'outline':0.0032},f'old_{i}.jpg',85)
  await e.stop()
  e=await Eng('tex_clean.jpg').start()
  await e.ev("()=>window.loadBVH('79_94','bvh/79_94.bvh')")
  for i,c in enumerate(cams): await e.shot({'t':0,'anim':{'name':'79_94','time':2.0,'t0':0},'cam':c,'outline':0.0014},f'new_{i}.jpg',85)
  await e.stop()
asyncio.run(main())
