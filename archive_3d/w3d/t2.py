import asyncio
from drv import Eng
async def main():
  e=await Eng().start()
  r=await e.ev('''()=>{let out=[];const THREE=null;
   let sk=null;window._m=null;
   return 0}''')
  await e.stop()
asyncio.run(main())
