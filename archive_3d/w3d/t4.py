import asyncio
from drv import Eng
MS=['quads','hams','glutes','calves','abs','obliques','lowback','pecs','delts','biceps','triceps','lats','traps','knees','ankles','hipjoint']
async def main():
  e=await Eng().start()
  await e.shot({'t':0},'v_front.jpg')
  for m in MS:
    back = m in ('hams','glutes','calves','lowback','lats','traps','triceps')
    await e.shot({'t':0.2,'muscles':{m:1},'charRotY':3.1416 if back else (0.5 if m in('obliques','delts','knees','ankles','hipjoint') else 0),'cam':{'pos':[0,1.0,4.2],'target':[0,0.95,0],'fov':30}},f'm_{m}.jpg',80)
  await e.stop()
asyncio.run(main())
