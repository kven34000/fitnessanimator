import asyncio
from drv import Eng
async def main():
  e=await Eng().start()
  for n in ['13_29','79_94','49_18','83_27','13_27','14_06']:
    d=await e.ev(f"()=>window.loadBVH('{n}','bvh/{n}.bvh')"); print(n,d)
  cam={'pos':[0,1.1,4.5],'target':[0,1.0,0],'fov':30}
  shots=[('sqA','13_29',32.0,0.6),('sqB','13_29',33.2,0.6),('sqC','13_29',34.0,0.6),('sqD','13_29',33.2,1.57),
         ('flex1','79_94',2.0,0),('flex2','79_94',5.0,0),('bal','49_18',4.0,0.3),('stair','83_27',3.0,1.57),('point','13_27',10.0,0.2),('sqE','14_06',10.5,0.6)]
  for nm,clip,t,ry in shots:
    await e.shot({'t':t,'anim':{'name':clip,'time':t,'t0':0},'charRotY':ry,'cam':cam},f'r_{nm}.jpg',75)
  await e.stop()
asyncio.run(main())
