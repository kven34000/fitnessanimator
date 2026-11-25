import asyncio, time
from drv import Eng
import poses as P
async def main():
  e=await Eng().start()
  t0=time.time()
  for i in range(30):
    t=i/30
    await e.pg.evaluate('(s)=>window.frame(s)',{'t':t,'pose':P.squat_cycle(t),'charRotY':0.6,'muscles':{'quads':1}})
    b=await e.pg.screenshot(type='jpeg',quality=90)
  print('per frame',(time.time()-t0)/30)
  open('sq_test.jpg','wb').write(b)
  await e.stop()
asyncio.run(main())
