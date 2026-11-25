import asyncio, math
from drv import Eng
import poses as P
async def main():
  e=await Eng().start()
  cam={'pos':[0,1.0,4.6],'target':[0,0.85,0],'fov':30}
  tests=[('sq0',P.squat(0.0),0.7),('sq5',P.squat(0.5),0.7),('sq1',P.squat(1.0),0.7),('sq1f',P.squat(1.0),0.0),
         ('bic',P.double_biceps(),0.0),('pt',P.point(),0.3),('th',P.think(),0.2),('cr',P.cross_arms(),0.2),('st',P.stand(),0.3),('run',P.run(0.1),1.4)]
  for n,pose,ry in tests:
    await e.shot({'t':0.3,'pose':pose,'charRotY':ry,'cam':cam,'muscles':{'quads':1} if n.startswith('sq') else ({'biceps':1} if n=='bic' else {})},f'p_{n}.jpg',80)
  await e.stop()
asyncio.run(main())
