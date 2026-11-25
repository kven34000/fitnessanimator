import asyncio
from drv import Eng
async def main():
  e=await Eng().start()
  await e.shot({'t':0,'debug':1,'bloom':0},'dbg_f.jpg')
  await e.shot({'t':0,'debug':1,'bloom':0,'charRotY':1.5708},'dbg_s.jpg')
  await e.stop()
asyncio.run(main())
