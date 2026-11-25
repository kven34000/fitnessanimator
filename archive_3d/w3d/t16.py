import asyncio
from drv import Eng
async def main():
  e=await Eng('tex_clean.jpg').start()
  print('tris',await e.ev("()=>window._shortsTris"))
  await e.ev("()=>window.loadBVH('13_29','bvh/13_29.bvh')")
  for i,(ry,t) in enumerate([(0.0,31.7),(0.9,33.1),(2.6,33.1),(0.4,34.0)]):
    await e.shot({'t':0,'anim':{'name':'13_29','time':t,'t0':31.7},'charRotY':ry,'cam':{'pos':[0,0.95,2.3],'target':[0,0.75,0],'fov':30},'outline':0.0014},f'sh_{i}.jpg',80)
  await e.stop()
asyncio.run(main())
