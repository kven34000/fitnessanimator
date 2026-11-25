import asyncio, time
from drv import Eng
import poses as P
async def main():
  e=await Eng().start()
  st={'t':0.3,'pose':P.squat_cycle(0.3),'charRotY':0.6,'muscles':{'quads':1}}
  t0=time.time()
  for i in range(10): await e.pg.evaluate('(s)=>window.frame(s)',st)
  t1=time.time()
  for i in range(10): await e.pg.screenshot(type='jpeg',quality=90)
  t2=time.time()
  for i in range(10): await e.pg.evaluate("()=>document.getElementById('c').toDataURL('image/jpeg',0.92).length")
  t3=time.time()
  print('render',(t1-t0)/10,'shot',(t2-t1)/10,'dataurl',(t3-t2)/10)
  await e.stop()
asyncio.run(main())
